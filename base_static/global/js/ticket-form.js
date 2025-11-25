document.addEventListener('DOMContentLoaded', function() {
    const categorySelect = document.getElementById('id_category');
    const subcategorySelect = document.getElementById('id_subcategory');
    const subcategoryInfo = document.getElementById('subcategory-info');
    
    if (!categorySelect || !subcategorySelect) return;
    
    if (typeof window.subcategoriesByCategory === 'undefined') {
        console.warn('subcategoriesByCategory não está definido');
        return;
    }
    
    let totalSubcategories = 0;
    for (let catId in window.subcategoriesByCategory) {
        totalSubcategories += window.subcategoriesByCategory[catId].length;
    }
    
    function updateSubcategories() {
        const categoryId = categorySelect.value;
        
        subcategorySelect.innerHTML = '<option value="">Selecione a subcategoria</option>';
        subcategorySelect.value = '';
        
        if (totalSubcategories === 0) {
            subcategorySelect.disabled = true;
            subcategorySelect.required = false;
            
            if (subcategoryInfo) {
                subcategoryInfo.textContent = 'Nenhuma subcategoria cadastrada no sistema.';
                subcategoryInfo.style.display = 'block';
            }
            return;
        }
        
        if (categoryId && window.subcategoriesByCategory[categoryId]) {
            const subcategories = window.subcategoriesByCategory[categoryId];
            
            if (subcategories.length > 0) {
                subcategories.forEach(function(subcat) {
                    const option = document.createElement('option');
                    option.value = subcat.id;
                    option.textContent = subcat.name;
                    subcategorySelect.appendChild(option);
                });
                
                subcategorySelect.disabled = false;
                subcategorySelect.required = true;
                if (subcategoryInfo) {
                    subcategoryInfo.style.display = 'none';
                }
            } else {
                subcategorySelect.disabled = true;
                subcategorySelect.required = false;
                if (subcategoryInfo) {
                    subcategoryInfo.textContent = 'Nenhuma subcategoria cadastrada para esta categoria.';
                    subcategoryInfo.style.display = 'block';
                }
            }
        } else {
            subcategorySelect.disabled = true;
            subcategorySelect.required = false;
            if (subcategoryInfo) {
                subcategoryInfo.style.display = 'none';
            }
        }
    }
    
    updateSubcategories();
    
    categorySelect.addEventListener('change', updateSubcategories);
});
