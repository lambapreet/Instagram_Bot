from django import forms
from comment.models import Comment

class NewCommentForm(forms.ModelForm):
    body = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Write a comment'}),
        required=True,
        label='',  # Optional: Hides the label in the form
    )

    class Meta:
        model = Comment
        fields = ("body",)
