"""The sqlalchemy model for a polloption."""
from sqlalchemy import (
    Column,
    func,
    ForeignKey,
)
from sqlalchemy.types import (
    BigInteger,
    Integer,
    DateTime,
    String,
)
from sqlalchemy.orm import relationship

from pollbot.db import base
from pollbot.helper.enums import ReferenceType


class Reference(base):
    """The model for a Reference."""

    __tablename__ = "reference"

    id = Column(Integer, primary_key=True)
    type = Column(String)
    bot_inline_message_id = Column(String)
    message_id = Column(BigInteger)

    # Keep those for now, in case we migrate to mtproto
    message_dc_id = Column(BigInteger)
    message_access_hash = Column(BigInteger)

    user_id = Column(
        BigInteger,
        ForeignKey("user.id", ondelete="cascade", name="user_fk"),
        nullable=True,
        index=True,
    )
    user = relationship("User", foreign_keys="Reference.user_id")

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # ManyToOne
    poll_id = Column(
        Integer,
        ForeignKey("poll.id", ondelete="cascade", name="reference_poll"),
        nullable=False,
        index=True,
    )
    poll = relationship("Poll")

    def __init__(
        self, poll, reference_type, user=None, message_id=None, inline_message_id=None,
    ):
        """Create a new poll."""
        self.poll = poll
        self.type = reference_type
        if (
            user is not None
            and message_id is not None
            and reference_type
            in [ReferenceType.admin.name, ReferenceType.private_vote.name]
        ):
            self.user = user
            self.message_id = message_id

        elif (
            inline_message_id is not None
            and reference_type == ReferenceType.inline.name
        ):
            self.bot_inline_message_id = inline_message_id
        else:
            raise Exception(
                "Tried to create Reference with wrong type or missing parameters"
            )

    def __repr__(self):
        """Print as string."""
        if self.type == ReferenceType.inline.name:
            message = f"Reference {self.id}: message_id {self.message_id}"
        elif self.type == ReferenceType.admin.name:
            message = f"Reference {self.id}: message_id {self.message_id}, admin: {self.user.id}"
        else:
            message = f"Reference {self.id}: message_id {self.message_id}, user: {self.user.id}"

        return message
