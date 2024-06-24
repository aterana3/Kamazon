document.addEventListener('DOMContentLoaded', function() {
    const imagePreview = document.getElementById('image-preview');

    if (existingImageUrl) {
        imagePreview.src = existingImageUrl;
    }

    imageInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.src = e.target.result;
            }
            reader.readAsDataURL(file);
        } else {
            imagePreview.src = imageDefault;
        }
    });

    const select = new Choices(categories, {
        removeItemButton: true,
        searchEnabled: true,
        searchChoices: true,
        placeholder: true,
        placeholderValue: 'Select a category',
        noResultsText: 'No results found',
        itemSelectText: 'Press to select',
        maxItemCount: 5,
        renderChoiceLimit: 5
    });
});