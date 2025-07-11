"""This module provides a session service that uses Google Firestore for session storage.

Classes:
    - FirebaseSessionService: A session service that uses Google Firestore for session storage.
"""
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_document import DocumentSnapshot

from app.utils.logger import Logger


class FirebaseSessionService:
    """A session service that uses Google Firestore for session storage."""

    def __init__(self, collection_name="sessions"):
        """Initializes the FirebaseSessionService.

        Args:
            collection_name (str): The name of the Firestore collection to use
                                   for sessions. Defaults to 'sessions'.
        """
        self.logger = Logger(__name__)
        self.collection_name = collection_name
        try:
            # Initialize Firebase if it hasn't been already
            if not firebase_admin._apps:
                cred = credentials.ApplicationDefault()
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
        except Exception as e:
            self.logger.error(f"Error initializing Firebase: {e}")
            self.db = None

    def create_session(self, session_id: str, data: dict):
        """Creates a new session document in Firestore.

        Args:
            session_id (str): The ID of the session.
            data (dict): The data to store in the session document.
        """
        if not self.db:
            self.logger.error("Firestore not initialized. Cannot create session.")
            return

        try:
            doc_ref = self.db.collection(self.collection_name).document(session_id)
            doc_ref.set(data)
            self.logger.info(f"Session '{session_id}' created successfully.")
        except Exception as e:
            self.logger.error(f"Error creating session '{session_id}': {e}")

    def get_session(self, session_id: str) -> dict | None:
        """Retrieves a session document from Firestore.

        Args:
            session_id (str): The ID of the session.

        Returns:
            dict or None: The session data as a dictionary if found, otherwise None.
        """
        if not self.db:
            self.logger.error("Firestore not initialized. Cannot get session.")
            return None

        try:
            doc_ref = self.db.collection(self.collection_name).document(session_id)
            doc: DocumentSnapshot = doc_ref.get()
            if doc.exists:
                self.logger.info(f"Session '{session_id}' retrieved successfully.")
                return doc.to_dict()
            else:
                self.logger.info(f"Session '{session_id}' not found.")
                return None
        except Exception as e:
            self.logger.error(f"Error getting session '{session_id}': {e}")
            return None

    def update_session(self, session_id: str, data: dict):
        """Updates a session document in Firestore.

        Args:
            session_id (str): The ID of the session.
            data (dict): The data to update in the session document.
        """
        if not self.db:
            self.logger.error("Firestore not initialized. Cannot update session.")
            return

        try:
            doc_ref = self.db.collection(self.collection_name).document(session_id)
            doc_ref.update(data)
            self.logger.info(f"Session '{session_id}' updated successfully.")
        except Exception as e:
            self.logger.error(f"Error updating session '{session_id}': {e}")

    def delete_session(self, session_id: str):
        """Deletes a session document from Firestore.

        Args:
            session_id (str): The ID of the session.
        """
        if not self.db:
            self.logger.error("Firestore not initialized. Cannot delete session.")
            return

        try:
            doc_ref = self.db.collection(self.collection_name).document(session_id)
            doc_ref.delete()
            self.logger.info(f"Session '{session_id}' deleted successfully.")
        except Exception as e:
            self.logger.error(f"Error deleting session '{session_id}': {e}")
