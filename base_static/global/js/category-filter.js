// Filtro dinâmico de categoria e subcategoria para páginas com filtros
document.addEventListener('DOMContentLoaded', function() {
    const categorySelect = document.getElementById('categorySelect');
    const subcategorySelect = document.getElementById('subcategorySelect');
    
    if (!categorySelect || !subcategorySelect) return;
    
    const allSubcategoryOptions = Array.from(subcategorySelect.querySelectorAll('option[data-category]'));
    
    function filterSubcategories() {
        const selectedCategory = categorySelect.value;
        const currentSubcategory = subcategorySelect.value;
        
        // Remove todas as opções exceto a primeira (placeholder)
        while (subcategorySelect.options.length > 1) {
            subcategorySelect.remove(1);
        }
        
        // Adiciona as subcategorias filtradas
        allSubcategoryOptions.forEach(option => {
            if (!selectedCategory || option.dataset.category === selectedCategory) {
                subcategorySelect.appendChild(option.cloneNode(true));
            }
        });
        
        // Restaura a seleção se ainda for válida
        if (currentSubcategory) {
            subcategorySelect.value = currentSubcategory;
        }
    }
    
    // Quando mudar a categoria, filtra as subcategorias
    categorySelect.addEventListener('change', function() {
        filterSubcategories();
    });
    
    // Quando selecionar uma subcategoria, preenche a categoria automaticamente
    subcategorySelect.addEventListener('change', function() {
        const selectedOption = subcategorySelect.options[subcategorySelect.selectedIndex];
        if (selectedOption && selectedOption.dataset.category) {
            categorySelect.value = selectedOption.dataset.category;
        }
    });
    
    // Aplica o filtro inicial ao carregar a página
    filterSubcategories();
});
