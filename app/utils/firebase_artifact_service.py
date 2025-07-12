"""This module provides a service that uses Firebase Storage for artifact storage.

Classes:
    - FirebaseArtifactService: A service that uses Firebase Storage for artifact storage.
    - default_user_id: The default user id.
    - logger: Logger instance.
"""
import os
import uuid
from typing import Optional

import firebase_admin
from firebase_admin import credentials, storage
from google.adk.artifacts import BaseArtifactService
from google.genai.types import Part

from app.utils.logger import Logger


class FirebaseArtifactService(BaseArtifactService):
    """A service that uses Firebase Storage for artifact storage."""

    def __init__(self, bucket_name: str):
        """Initializes the FirebaseArtifactService.

        Args:
            bucket_name: The name of the Firebase Storage bucket.
        """
        self.logger = Logger(__name__)
        self.bucket_name = bucket_name
        try:
            # Initialize Firebase if it hasn't been already
            if not firebase_admin._apps:
                cred = credentials.ApplicationDefault()
                firebase_admin.initialize_app(cred)
            self.bucket = storage.bucket(name=bucket_name)
        except Exception as e:
            self.logger.error(f"Error initializing Firebase Storage: {e}")
            self.bucket = None

    async def save_artifact(self, artifact: Optional[Part], user_id: str, session_id: str, artifact_key: str | None = None) -> str:
        """Saves an artifact to Firebase Storage.

        Args:
            artifact: The artifact to save.
            user_id: The ID of the user.
            session_id: The ID of the session.
            artifact_key: An optional key for the artifact. If None, a UUID will be generated.

        Returns:
            The artifact key.
        """
        if not self.bucket:
            self.logger.error("Firebase Storage not initialized. Cannot save artifact.")
            return ""

        try:
            if artifact_key is None:
                artifact_key = str(uuid.uuid4())

            # Firebase Storage doesn't have explicit versioning like GCS versioning.
            # A common approach is to include a timestamp or version in the blob name
            # or use separate folders for versions. For simplicity here, we'll
            # overwrite if the key exists or create a new one.
            # If real versioning is needed, a different strategy would be required.
            blob_name = f"artifacts/{user_id}/{session_id}/{artifact_key}"
            blob = self.bucket.blob(blob_name)

            # Upload the artifact data (assuming artifact.data is bytes)
            blob.upload_from_string(artifact.data, content_type=artifact.mime_type)

            self.logger.info(f"Artifact with key '{artifact_key}' saved successfully to '{blob_name}'.")
            return artifact_key
        except Exception as e:
            self.logger.error(f"Error saving artifact with key '{artifact_key}': {e}")
            raise # Re-raise the exception

    async def load_artifact(self, user_id: str, session_id: str, artifact_key: str, version: str | None = None) -> Optional[Part]:
        """Loads an artifact from Firebase Storage.

        Args:
            user_id: The ID of the user.
            session_id: The ID of the session.
            artifact_key: The key of the artifact.
            version: Optional version of the artifact. Not directly supported by
                     this simple implementation's blob naming.

        Returns:
            The loaded Artifact.
        """
        if version is not None:
            self.logger.warning("Versioning not directly supported in this Firebase Storage implementation. Loading latest.")

        return await self.download_artifact(artifact_id=artifact_key, user_id=user_id, session_id=session_id)

    async def list_artifact_keys(self, user_id: str, session_id: str) -> list[str]:
        """Lists artifact keys for a session in Firebase Storage.

        Args:
            user_id: The ID of the user.
            session_id: The ID of the session.

        Returns:
            A list of artifact keys.
        """
        artifacts = await self._list_artifacts_internal(user_id, session_id)
        return [artifact.id for artifact in artifacts if artifact.id]

    async def upload_artifact(self, artifact: Optional[Part], user_id: str, session_id: str) -> str:
        """Uploads an artifact to Firebase Storage.

        Args:
            artifact: The artifact to upload.
            user_id: The ID of the user.
            session_id: The ID of the session.

        Returns:
            The artifact ID (Firebase Storage blob name).
        """
        if not self.bucket:
            self.logger.error("Firebase Storage not initialized. Cannot upload artifact.")
            return ""

        # This method seems redundant with save_artifact.
        # Assuming artifact.id is intended as the artifact_key here.
        # This might indicate a slight mismatch between ADK's artifact model
        # and a simple key/value storage like Firebase Storage.
        try:
            blob_name = f"artifacts/{user_id}/{session_id}/{artifact.id}"
            blob = self.bucket.blob(blob_name)

            # Upload the artifact data (assuming artifact.data is bytes)
            blob.upload_from_string(artifact.data, content_type=artifact.mime_type)

            self.logger.info(f"Artifact '{artifact.id}' uploaded successfully to '{blob_name}'.")
            return artifact.id
        except Exception as e:
            self.logger.error(f"Error uploading artifact '{artifact.id}': {e}")
            raise # Re-raise the exception

    async def download_artifact(self, artifact_id: str, user_id: str, session_id: str) -> Optional[Part]:
        """Downloads an artifact from Firebase Storage.

        Args:
            artifact_id: The ID of the artifact (Firebase Storage blob name).
            user_id: The ID of the user.
            session_id: The ID of the session.

        Returns:
            The downloaded Artifact.

        Raises:
            FileNotFoundError: If the artifact is not found.
            Exception: If there's an error during download.
        """
        if not self.bucket:
            self.logger.error("Firebase Storage not initialized. Cannot download artifact.")
            raise Exception("Firebase Storage not initialized.")

        try:
            # Construct the blob name
            blob_name = f"artifacts/{user_id}/{session_id}/{artifact_id}"
            blob = self.bucket.blob(blob_name)

            if not blob.exists():
                raise FileNotFoundError(f"Artifact '{artifact_id}' not found at '{blob_name}'.")

            # Download the artifact data
            artifact_data = blob.download_as_bytes()
            # Assuming artifact.mime_type can be retrieved from metadata or inferred
            mime_type = blob.content_type or "application/octet-stream"

            self.logger.info(f"Artifact '{artifact_id}' downloaded successfully from '{blob_name}'.")
            return Part(data=artifact_data, mime_type=mime_type, id=artifact_id)
        except FileNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error downloading artifact '{artifact_id}': {e}")
            raise # Re-raise the exception

    async def list_artifacts(self, user_id: str, session_id: str) -> list[Optional[Part]]:
        """Lists artifacts for a session in Firebase Storage.

        Args:
            user_id: The ID of the user.
            session_id: The ID of the session.

        Returns:
            A list of Artifacts.
        """
        # This method name is not part of the BaseArtifactService as per the list provided.
        # Keeping it for potential utility or if it was intended to be implemented.
        return await self._list_artifacts_internal(user_id, session_id)

    async def _list_artifacts_internal(self, user_id: str, session_id: str) -> list[Optional[Part]]:
        """Lists artifacts for a session in Firebase Storage.

        Args:
            user_id: The ID of the user.
            session_id: The ID of the session.

        Returns:
            A list of Artifacts.
        """
        if not self.bucket:
            self.logger.error("Firebase Storage not initialized. Cannot list artifacts.")
            return []

        try:
            # List blobs in the session's artifact folder
            prefix = f"artifacts/{user_id}/{session_id}/"
            blobs = self.bucket.list_blobs(prefix=prefix)

            artifacts: list[Optional[Part]] = []
            for blob in blobs:
                # Extract artifact ID from blob name
                artifact_id = os.path.basename(blob.name)
                # We can't download the full data here for performance, so create Artifacts with basic info
                # You might need to modify this based on how Artifact is used by the ADK
                blob_data = blob.download_as_text()
                artifacts.append(Part(id=artifact_id, data=blob_data, mime_type=blob.content_type))

            self.logger.info(f"Listed {len(artifacts)} artifacts for session '{session_id}'.")
            return artifacts
        except Exception as e:
            self.logger.error(f"Error listing artifacts for session '{session_id}': {e}")
            return []

    async def list_versions(self, user_id: str, session_id: str, artifact_key: str) -> list[str]:
        """Lists versions for a specific artifact key.

        Args:
            user_id: The ID of the user.
            session_id: The ID of the session.
            artifact_key: The key of the artifact.

        Returns:
            A list of version identifiers.
        """
        # This simple Firebase Storage implementation doesn't directly support versioning
        # in the way that might be expected by list_versions.
        self.logger.warning("Versioning not directly supported in this Firebase Storage implementation. list_versions will return an empty list.")
        return []