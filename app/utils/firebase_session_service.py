"""This module provides a session service that uses Google Firestore for session storage.

Classes:
    - FirebaseSessionService: A session service that uses Google Firestore for session storage.
"""
import firebase_admin
from firebase_admin import credentials, firestore
from google.adk.sessions import BaseSessionService, SessionEvent
from google.cloud.firestore_v1.base_document import DocumentSnapshot

from app.utils.logger import Logger


class FirebaseSessionService(BaseSessionService):
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

    async def create_session(self, user_id: str, session_id: str, data: dict):
        """Creates a new session document in Firestore.

        Args:
            session_id (str): The ID of the session.
            data (dict): The data to store in the session document.
        """
        if not self.db:
            self.logger.error("Firestore not initialized. Cannot create session.")
            return

        try:
            doc_ref = self.db.collection(self.collection_name).document(f"{user_id}:{session_id}")
            doc_ref.set(data)
            self.logger.info(f"Session '{session_id}' created successfully.")
        except Exception as e:
            self.logger.error(f"Error creating session '{session_id}': {e}")
            raise # Re-raise the exception to be handled by the caller

    async def get_session(self, user_id: str, session_id: str) -> dict | None:
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
            doc_ref = self.db.collection(self.collection_name).document(f"{user_id}:{session_id}")
            doc: DocumentSnapshot = doc_ref.get()
            if doc.exists:
                self.logger.info(f"Session '{session_id}' retrieved successfully.")
                return doc.to_dict()
            else:
                self.logger.info(f"Session '{session_id}' not found.")
                return None
        except Exception as e:
            self.logger.error(f"Error getting session '{session_id}': {e}")
            raise # Re-raise the exception to be handled by the caller

    async def update_session(self, user_id: str, session_id: str, data: dict):
        """Updates a session document in Firestore.

        Args:
            session_id (str): The ID of the session.
            data (dict): The data to update in the session document.
        """
        if not self.db:
            self.logger.error("Firestore not initialized. Cannot update session.")
            return

        try:
            doc_ref = self.db.collection(self.collection_name).document(f"{user_id}:{session_id}")
            doc_ref.update(data)
            self.logger.info(f"Session '{session_id}' updated successfully.")
        except Exception as e:
            self.logger.error(f"Error updating session '{session_id}': {e}")
            raise # Re-raise the exception to be handled by the caller

    async def delete_session(self, user_id: str, session_id: str):
        """Deletes a session document from Firestore.

        Args:
            session_id (str): The ID of the session.
        """
        if not self.db:
            self.logger.error("Firestore not initialized. Cannot delete session.")
            return

        try:
            doc_ref = self.db.collection(self.collection_name).document(f"{user_id}:{session_id}")
            doc_ref.delete()
            self.logger.info(f"Session '{session_id}' deleted successfully.")
        except Exception as e:
            self.logger.error(f"Error deleting session '{session_id}': {e}")
            raise # Re-raise the exception to be handled by the caller

    async def _get_session_doc_ref(self, user_id: str, session_id: str):
        """Gets the document reference for a session."""
        if not self.db:
            self.logger.error("Firestore not initialized. Cannot get document reference.")
            return None
        return self.db.collection(self.collection_name).document(f"{user_id}:{session_id}")

    async def append_event(self, user_id: str, session_id: str, event: SessionEvent):
        """Appends a session event.

        Args:
            user_id: The user ID.
            session_id: The session ID.
            event: The session event to append.
        """
        if not self.db:
            self.logger.error("Firestore not initialized. Cannot append event.")
            return

        try:
            session_doc_ref = await self._get_session_doc_ref(user_id, session_id)
            if session_doc_ref:
                events_collection_ref = session_doc_ref.collection("events")
                # You might want to add a timestamp or a unique ID to the event data
                event_data = event.model_dump() # Assuming SessionEvent is a Pydantic model
                await events_collection_ref.add(event_data)
                self.logger.info(f"Event appended to session '{session_id}'.")
            else:
                self.logger.warning(f"Session document for '{session_id}' not found. Cannot append event.")
        except Exception as e:
            self.logger.error(f"Error appending event to session '{session_id}': {e}")
            raise # Re-raise the exception to be handled by the caller

    async def list_events(self, user_id: str, session_id: str) -> list[SessionEvent]:
        """Lists session events.

        Returns:
            A list of SessionEvent objects.
        """
        if not self.db:
            self.logger.error("Firestore not initialized. Cannot list events.")
            return []

        try:
            session_doc_ref = await self._get_session_doc_ref(user_id, session_id)
            if session_doc_ref:
                events_collection_ref = session_doc_ref.collection("events")
                events_docs = await events_collection_ref.get()
                # Convert Firestore documents to SessionEvent objects
                session_events = [SessionEvent(**doc.to_dict()) for doc in events_docs]
                self.logger.info(f"Listed {len(session_events)} events for session '{session_id}'.")
                return session_events
            else:
                self.logger.warning(f"Session document for '{session_id}' not found. Cannot list events.")
                return []
        except Exception as e:
            self.logger.error(f"Error listing events for session '{session_id}': {e}")
            raise # Re-raise the exception to be handled by the caller

    async def list_sessions(self, user_id: str) -> list[dict]:
        """Lists sessions for a user.

        Returns:
            A list of session dictionaries.
        """
        if not self.db:
            self.logger.error("Firestore not initialized. Cannot list sessions.")
            return []

        try:
            # Query for documents where the document ID starts with user_id
            sessions_query = self.db.collection(self.collection_name).where(firestore.FieldPath.document_id(), ">=", user_id + ":").where(firestore.FieldPath.document_id(), "<", user_id + ";")
            sessions_docs = await sessions_query.get()
            # Convert Firestore documents to dictionaries
            session_list = [doc.to_dict() for doc in sessions_docs]
            self.logger.info(f"Listed {len(session_list)} sessions for user '{user_id}'.")
            return session_list
        except Exception as e:
            self.logger.error(f"Error listing sessions for user '{user_id}': {e}")
            raise # Re-raise the exception to be handled by the caller
