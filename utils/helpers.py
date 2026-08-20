from pathlib import Path


UPLOAD_DIRECTORY = Path(
    "data/uploads"
)


def save_uploaded_file(uploaded_file):

    UPLOAD_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = (
        UPLOAD_DIRECTORY
        / uploaded_file.name
    )

    with open(file_path, "wb") as file:

        file.write(
            uploaded_file.getbuffer()
        )

    return file_path