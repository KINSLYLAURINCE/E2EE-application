from django.db import models
from django.contrib.auth.models import User

class UserPublicKey(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='public_key_info')
    public_key = models.TextField()
    encrypted_private_key = models.TextField(null=True, blank=True)
    salt = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s public key"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    # Encrypted for the recipient to read
    encrypted_for_recipient = models.TextField()
    # Encrypted for the sender to read their own history
    encrypted_for_sender = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"From {self.sender.username} to {self.recipient.username} at {self.timestamp}"
