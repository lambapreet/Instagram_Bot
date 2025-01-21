from django import forms
from post.models import Post

class NewPostForm(forms.ModelForm):  # Fixed the class name to follow proper naming conventions
    picture = forms.ImageField(required=True)
    caption = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Caption'}),
        required=True
    )
    tags = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Tags | Separate with commas'}),
        required=True
    )

    class Meta:
        model = Post
        fields = ['picture', 'caption', 'tags']
