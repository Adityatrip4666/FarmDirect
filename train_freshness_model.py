from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras import layers


DATA_DIR = Path("data/freshness_raw/Processed Data")
MODEL_DIR = Path("models")

MODEL_PATH = MODEL_DIR / "freshness_model.keras"
LABELS_PATH = MODEL_DIR / "freshness_labels.json"
METRICS_PATH = MODEL_DIR / "freshness_metrics.json"

IMG_HEIGHT = 224
IMG_WIDTH = 224
BATCH_SIZE = 32
SEED = 42

INITIAL_EPOCHS = 6
FINE_TUNE_EPOCHS = 3

CLASS_NAMES = [
    "Fresh",
    "Moderately Fresh",
    "Not Fresh",
]

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def map_folder_to_label(folder_name: str) -> int:
    """Convert the dataset's folder name to one of the 3 FarmDirect labels."""
    name = folder_name.strip().lower()

    if name.startswith("fresh "):
        return 0

    if name.startswith("semi"):
        return 1

    if name.startswith("rotten "):
        return 2

    raise ValueError(f"Unknown freshness folder: {folder_name}")


def source_group_name(path: Path) -> str:
    """
    Group augmented images back with their apparent source image.

    Example:
        aug_105_IMG_20251102_081029133_AE.jpg
    becomes:
        IMG_20251102_081029133_AE
    """
    return re.sub(
        r"^aug_\d+_",
        "",
        path.stem,
        flags=re.IGNORECASE,
    )


def collect_dataset():
    """Collect valid image paths and split by source-image groups."""
    if not DATA_DIR.exists():
        raise FileNotFoundError(
            f"Dataset directory not found: {DATA_DIR}"
        )

    groups_by_label = {
        0: defaultdict(list),
        1: defaultdict(list),
        2: defaultdict(list),
    }

    skipped_images = []

    folders = [
        folder
        for folder in DATA_DIR.iterdir()
        if folder.is_dir()
    ]

    if len(folders) != 24:
        raise ValueError(
            f"Expected 24 dataset folders, found {len(folders)}."
        )

    for folder in sorted(folders, key=lambda item: item.name.lower()):
        label = map_folder_to_label(folder.name)

        for image_path in sorted(folder.rglob("*")):
            if not image_path.is_file():
                continue

            if image_path.suffix.lower() not in VALID_EXTENSIONS:
                continue

            try:
                with Image.open(image_path) as image:
                    image.verify()
            except Exception:
                skipped_images.append(str(image_path))
                continue

            group_key = (
                folder.name,
                source_group_name(image_path),
            )

            groups_by_label[label][group_key].append(
                str(image_path)
            )

    rng = np.random.default_rng(SEED)

    train_paths = []
    train_labels = []

    val_paths = []
    val_labels = []

    test_paths = []
    test_labels = []

    for label in range(3):
        groups = list(groups_by_label[label].values())

        if len(groups) < 3:
            raise ValueError(
                f"Not enough source groups for class "
                f"{CLASS_NAMES[label]}: {len(groups)}"
            )

        rng.shuffle(groups)

        total_groups = len(groups)

        train_group_count = max(
            1,
            int(round(total_groups * 0.80))
        )

        val_group_count = max(
            1,
            int(round(total_groups * 0.10))
        )

        if train_group_count + val_group_count >= total_groups:
            train_group_count = max(1, total_groups - 2)
            val_group_count = 1

        test_group_count = (
            total_groups
            - train_group_count
            - val_group_count
        )

        if test_group_count < 1:
            raise ValueError(
                f"Could not create test split for "
                f"{CLASS_NAMES[label]}"
            )

        train_groups = groups[:train_group_count]

        val_groups = groups[
            train_group_count:
            train_group_count + val_group_count
        ]

        test_groups = groups[
            train_group_count + val_group_count:
        ]

        for group in train_groups:
            train_paths.extend(group)
            train_labels.extend([label] * len(group))

        for group in val_groups:
            val_paths.extend(group)
            val_labels.extend([label] * len(group))

        for group in test_groups:
            test_paths.extend(group)
            test_labels.extend([label] * len(group))

    train_order = rng.permutation(len(train_paths))
    val_order = rng.permutation(len(val_paths))
    test_order = rng.permutation(len(test_paths))

    train_paths = [train_paths[i] for i in train_order]
    train_labels = [train_labels[i] for i in train_order]

    val_paths = [val_paths[i] for i in val_order]
    val_labels = [val_labels[i] for i in val_order]

    test_paths = [test_paths[i] for i in test_order]
    test_labels = [test_labels[i] for i in test_order]

    return (
        train_paths,
        train_labels,
        val_paths,
        val_labels,
        test_paths,
        test_labels,
        skipped_images,
    )


def load_image(path, label):
    image_data = tf.io.read_file(path)

    image = tf.io.decode_image(
        image_data,
        channels=3,
        expand_animations=False,
    )

    image.set_shape([None, None, 3])

    image = tf.image.resize(
        image,
        [IMG_HEIGHT, IMG_WIDTH],
    )

    image = tf.cast(image, tf.float32)

    return image, label


def make_dataset(paths, labels, training=False):
    dataset = tf.data.Dataset.from_tensor_slices(
        (
            paths,
            np.asarray(labels, dtype=np.int32),
        )
    )

    if training:
        dataset = dataset.shuffle(
            buffer_size=len(paths),
            seed=SEED,
            reshuffle_each_iteration=True,
        )

    dataset = dataset.map(
        load_image,
        num_parallel_calls=tf.data.AUTOTUNE,
    )

    dataset = dataset.batch(BATCH_SIZE)

    dataset = dataset.prefetch(tf.data.AUTOTUNE)

    return dataset


def build_model():
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(IMG_HEIGHT, IMG_WIDTH, 3),
        include_top=False,
        weights="imagenet",
    )

    base_model.trainable = False

    inputs = layers.Input(
        shape=(IMG_HEIGHT, IMG_WIDTH, 3),
        name="image",
    )

    x = layers.RandomFlip(
        "horizontal",
        name="random_flip",
    )(inputs)

    x = layers.RandomRotation(
        0.05,
        name="random_rotation",
    )(x)

    x = layers.RandomZoom(
        0.10,
        name="random_zoom",
    )(x)

    x = layers.RandomContrast(
        0.10,
        name="random_contrast",
    )(x)

    # MobileNetV2 expects pixels scaled to [-1, 1].
    x = layers.Rescaling(
        1.0 / 127.5,
        offset=-1.0,
        name="mobilenet_v2_scaling",
    )(x)

    x = base_model(
        x,
        training=False,
    )

    x = layers.GlobalAveragePooling2D(
        name="global_average_pooling",
    )(x)

    x = layers.Dropout(
        0.25,
        name="dropout",
    )(x)

    outputs = layers.Dense(
        3,
        activation="softmax",
        name="freshness_output",
    )(x)

    model = tf.keras.Model(
        inputs,
        outputs,
        name="farmdirect_freshness_model",
    )

    model.compile(
        optimizer=tf.keras.optimizers.Adam(
            learning_rate=1e-3
        ),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    return model, base_model


def calculate_metrics(model, test_dataset, test_labels):
    probabilities = model.predict(
        test_dataset,
        verbose=0,
    )

    predictions = np.argmax(
        probabilities,
        axis=1,
    )

    true_labels = np.asarray(
        test_labels,
        dtype=np.int32,
    )

    confusion_matrix = tf.math.confusion_matrix(
        true_labels,
        predictions,
        num_classes=3,
    ).numpy()

    per_class = {}

    for index, class_name in enumerate(CLASS_NAMES):
        true_positive = confusion_matrix[
            index, index
        ]

        support = confusion_matrix[
            index
        ].sum()

        predicted_count = confusion_matrix[
            :, index
        ].sum()

        precision = (
            float(true_positive / predicted_count)
            if predicted_count
            else 0.0
        )

        recall = (
            float(true_positive / support)
            if support
            else 0.0
        )

        per_class[class_name] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "support": int(support),
        }

    accuracy = float(
        np.mean(predictions == true_labels)
    )

    return {
        "test_accuracy": round(accuracy, 4),
        "confusion_matrix": confusion_matrix.tolist(),
        "per_class": per_class,
    }


def main():
    tf.keras.utils.set_random_seed(SEED)

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    (
        train_paths,
        train_labels,
        val_paths,
        val_labels,
        test_paths,
        test_labels,
        skipped_images,
    ) = collect_dataset()

    print()
    print("FarmDirect Freshness Model Training")
    print("=" * 45)
    print(f"Fresh images:             {train_labels.count(0) + val_labels.count(0) + test_labels.count(0)}")
    print(f"Moderately Fresh images:  {train_labels.count(1) + val_labels.count(1) + test_labels.count(1)}")
    print(f"Not Fresh images:         {train_labels.count(2) + val_labels.count(2) + test_labels.count(2)}")
    print()
    print(f"Training images:          {len(train_paths)}")
    print(f"Validation images:        {len(val_paths)}")
    print(f"Test images:              {len(test_paths)}")
    print(f"Skipped/corrupt images:   {len(skipped_images)}")
    print()

    train_dataset = make_dataset(
        train_paths,
        train_labels,
        training=True,
    )

    val_dataset = make_dataset(
        val_paths,
        val_labels,
        training=False,
    )

    test_dataset = make_dataset(
        test_paths,
        test_labels,
        training=False,
    )

    model, base_model = build_model()

    checkpoint = tf.keras.callbacks.ModelCheckpoint(
        filepath=str(MODEL_PATH),
        monitor="val_accuracy",
        mode="max",
        save_best_only=True,
        verbose=1,
    )

    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor="val_accuracy",
        mode="max",
        patience=2,
        restore_best_weights=True,
        verbose=1,
    )

    reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.5,
        patience=1,
        min_lr=1e-6,
        verbose=1,
    )

    print("Starting transfer-learning phase...")
    print()

    model.fit(
        train_dataset,
        validation_data=val_dataset,
        epochs=INITIAL_EPOCHS,
        callbacks=[
            checkpoint,
            early_stopping,
            reduce_lr,
        ],
        verbose=1,
    )

    print()
    print("Starting fine-tuning phase...")
    print()

    base_model.trainable = True

    for layer in base_model.layers[:-30]:
        layer.trainable = False

    for layer in base_model.layers[-30:]:
        if isinstance(
            layer,
            layers.BatchNormalization,
        ):
            layer.trainable = False
        else:
            layer.trainable = True

    model.compile(
        optimizer=tf.keras.optimizers.Adam(
            learning_rate=1e-5
        ),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    model.fit(
        train_dataset,
        validation_data=val_dataset,
        epochs=FINE_TUNE_EPOCHS,
        callbacks=[
            checkpoint,
            early_stopping,
            reduce_lr,
        ],
        verbose=1,
    )

    print()
    print("Loading best saved model...")
    print()

    model = tf.keras.models.load_model(
        MODEL_PATH,
        compile=False,
    )

    model.compile(
        optimizer=tf.keras.optimizers.Adam(
            learning_rate=1e-5
        ),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    test_loss, test_accuracy = model.evaluate(
        test_dataset,
        verbose=1,
    )

    metrics = calculate_metrics(
        model,
        test_dataset,
        test_labels,
    )

    metrics["test_loss"] = round(
        float(test_loss),
        4,
    )

    metrics["test_accuracy"] = round(
        float(test_accuracy),
        4,
    )

    with open(
        LABELS_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            {
                "class_names": CLASS_NAMES
            },
            file,
            indent=2,
        )

    with open(
        METRICS_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            {
                "image_size": [
                    IMG_HEIGHT,
                    IMG_WIDTH,
                ],
                "classes": CLASS_NAMES,
                "train_images": len(train_paths),
                "validation_images": len(val_paths),
                "test_images": len(test_paths),
                "skipped_images": len(skipped_images),
                **metrics,
            },
            file,
            indent=2,
        )

    print()
    print("=" * 45)
    print("TRAINING COMPLETE")
    print("=" * 45)
    print(
        f"Test accuracy: {metrics['test_accuracy'] * 100:.2f}%"
    )
    print()
    print("Per-class metrics:")

    for class_name, values in metrics["per_class"].items():
        print(
            f"  {class_name}: "
            f"precision={values['precision']:.4f}, "
            f"recall={values['recall']:.4f}, "
            f"support={values['support']}"
        )

    print()
    print(f"Model:   {MODEL_PATH}")
    print(f"Labels:  {LABELS_PATH}")
    print(f"Metrics: {METRICS_PATH}")
    print()


if __name__ == "__main__":
    main()