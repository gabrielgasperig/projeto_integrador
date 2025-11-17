document.addEventListener('DOMContentLoaded', function() {
    const categorySelect = document.getElementById('categorySelect');
    const subcategorySelect = document.getElementById('subcategorySelect');
    
    if (!categorySelect || !subcategorySelect) return;
    
    const allSubcategoryOptions = Array.from(subcategorySelect.querySelectorAll('option[data-category]'));
    
    function filterSubcategories() {
        const selectedCategory = categorySelect.value;
        const currentSubcategory = subcategorySelect.value;
        
        while (subcategorySelect.options.length > 1) {
            subcategorySelect.remove(1);
        }
        
        allSubcategoryOptions.forEach(option => {
            if (!selectedCategory || option.dataset.category === selectedCategory) {
                subcategorySelect.appendChild(option.cloneNode(true));
            }
        });
        
        if (currentSubcategory) {
            subcategorySelect.value = currentSubcategory;
        }
    }
    
    categorySelect.addEventListener('change', function() {
        filterSubcategories();
    });
    
    subcategorySelect.addEventListener('change', function() {
        const selectedOption = subcategorySelect.options[subcategorySelect.selectedIndex];
        if (selectedOption && selectedOption.dataset.category) {
            categorySelect.value = selectedOption.dataset.category;
        }
    });
    
    filterSubcategories();
});
