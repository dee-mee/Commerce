from django import forms
from django.forms import inlineformset_factory
from .models import Review, ReviewImage

class ReviewForm(forms.ModelForm):
    """Form for product reviews"""
    rating = forms.IntegerField(widget=forms.HiddenInput(attrs={'id': 'rating-input'}))
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Share your experience with this product. What did you like or dislike?'}),
        }

# Create a formset for review images
ReviewImageFormSet = inlineformset_factory(
    Review,
    ReviewImage,
    fields=['image'],
    extra=3,
    can_delete=False,
    widgets={
        'image': forms.FileInput(attrs={'class': 'form-control'})
    }
)
