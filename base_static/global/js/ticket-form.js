document.addEventListener('DOMContentLoaded', function() {
    const categorySelect = document.getElementById('id_category');
    const subcategoryField = document.getElementById('subcategory-field');
    const subcategorySelect = document.getElementById('id_subcategory');
    const subcategoryRequired = document.getElementById('subcategory-required');
    
    if (!categorySelect || !subcategorySelect) return;
    
    // Esta função espera que subcategoriesByCategory seja definido globalmente
    if (typeof window.subcategoriesByCategory === 'undefined') {
        console.warn('subcategoriesByCategory não está definido');
        return;
    }
    
    function updateSubcategories() {
        const categoryId = categorySelect.value;
        
        // Limpa as opções atuais
        subcategorySelect.innerHTML = '<option value="">Selecione a subcategoria</option>';
        
        if (categoryId && window.subcategoriesByCategory[categoryId]) {
            const subcategories = window.subcategoriesByCategory[categoryId];
            
            if (subcategories.length > 0) {
                // Adiciona as subcategorias
                subcategories.forEach(function(subcat) {
                    const option = document.createElement('option');
                    option.value = subcat.id;
                    option.textContent = subcat.name;
                    subcategorySelect.appendChild(option);
                });
                
                // Mostra o campo e marca como obrigatório
                subcategoryField.style.display = 'block';
                subcategorySelect.required = true;
                subcategoryRequired.style.display = 'inline';
            } else {
                // Esconde o campo se não há subcategorias
                subcategoryField.style.display = 'none';
                subcategorySelect.required = false;
                subcategoryRequired.style.display = 'none';
            }
        } else {
            // Esconde o campo se nenhuma categoria selecionada
            subcategoryField.style.display = 'none';
            subcategorySelect.required = false;
            subcategoryRequired.style.display = 'none';
        }
    }
    
    // Executa ao carregar a página (caso já tenha categoria selecionada)
    updateSubcategories();
    
    // Escuta mudanças na categoria
    categorySelect.addEventListener('change', updateSubcategories);
});
