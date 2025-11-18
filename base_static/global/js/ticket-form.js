document.addEventListener('DOMContentLoaded', function() {
    const categorySelect = document.getElementById('id_category');
    const subcategoryField = document.getElementById('subcategory-field');
    const subcategorySelect = document.getElementById('id_subcategory');
    const subcategoryRequired = document.getElementById('subcategory-required');
    
    if (!categorySelect || !subcategorySelect) return;
    
    if (typeof window.subcategoriesByCategory === 'undefined') {
        console.warn('subcategoriesByCategory não está definido');
        return;
    }
    
    function updateSubcategories() {
        const categoryId = categorySelect.value;
        
    subcategorySelect.innerHTML = '<option value="">Selecione a subcategoria</option>';
    subcategorySelect.value = '';
        
        if (categoryId && window.subcategoriesByCategory[categoryId]) {
            const subcategories = window.subcategoriesByCategory[categoryId];
            
            if (subcategories.length > 0) {
                subcategories.forEach(function(subcat) {
                    const option = document.createElement('option');
                    option.value = subcat.id;
                    option.textContent = subcat.name;
                    subcategorySelect.appendChild(option);
                });
                
                subcategoryField.style.display = 'block';
                subcategorySelect.required = true;
                if (subcategoryRequired) {
                    subcategoryRequired.style.display = 'inline';
                }
            } else {
                subcategoryField.style.display = 'none';
                subcategorySelect.required = false;
                if (subcategoryRequired) {
                    subcategoryRequired.style.display = 'none';
                }
            }
        } else {
            subcategoryField.style.display = 'none';
            subcategorySelect.required = false;
            if (subcategoryRequired) {
                subcategoryRequired.style.display = 'none';
            }
        }
    }
    
    updateSubcategories();
    
    categorySelect.addEventListener('change', updateSubcategories);
});
