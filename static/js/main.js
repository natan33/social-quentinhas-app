// Global variables
let editingId = null;

$(document).ready(function() {
    // Armazena a instância da tabela em uma variável
    var table = $('#vendasTable').DataTable({
        searching: false,
        lengthChange: false,
        responsive: true,
        pagingType: "simple_numbers",
        order: [[9, 'desc']],
        
        ajax: {
            url: '/api/vendas',
            data: function(d) {
                d.vendedor = $('#vendedor').val();
                d.comprador = $('#comprador').val();
                d.id = $('#id').val();
            },
            dataSrc: ''
        },
        
        columns: [
            { data: 'id' },
            { data: 'nome_produto' },
            { data: 'nome_vendedor' },
            { data: 'nome_comprador' },
            { 
                data: 'grupo',
                render: function(data) {
                    if(data === 'M') return '<span class="badge bg-success">Meninos</span>';
                    else if(data === 'F') return '<span class="badge bg-danger">Meninas</span>';
                    else return '<span class="badge bg-warning">Igreja</span>';
                }
            },
            { data: 'quantidade' },
            { data: 'preco_unitario' },
            { data: 'valor_total' },
            { 
                data: 'status_pagamento',
                render: function(data) {
                    if(data === 'Pago')
                        return '<span class="badge bg-success">Pago</span>';
                    else
                        return '<span class="badge bg-danger">Pendente</span>';
                }
            },
            { data: 'data_venda' },
            {
                data: 'id',
                orderable: false,
                render: function(id) {
                    return `
                        <div class="btn-group" role="group">
                            <button type="button" class="btn btn-sm btn-warning" onclick="editarVenda('${id}')" title="Editar">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button type="button" class="btn btn-sm btn-danger" onclick="confirmarExclusao('${id}')" title="Excluir">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    `;
                }
            }
        ]
    });

    // Botão "Filtrar" usa a instância correta da tabela
    $('#btnFiltrar').on('click', function() {
        table.ajax.reload();
    });

    // Botão "Limpar"
    $('#btnLimpar').on('click', function() {
        $('#filtrosForm')[0].reset();
        table.ajax.reload();
    });
});


 $(document).ready(function() {
    $('#filter_vendedor').select2({
      theme:"bootstrap-5",
      width:$("#filter_vendedor").data("width")
      ? $("#filter_vendedor").data("width")
      :$("#filter_vendedor").hasClass("w-100")
      ? "100%"
      : "style",
      placeholder: $("#filter_vendedor").data('placeholder'),
      closeOnSelect: false,
      maximumSelectionLength: 3,
      ajax: {
        url: '/api/filter_vendedor',
        dataType: 'json',
        delay: 250,
        data: function(params){
            var query = {
                serch : params.term,
                type:"internal"
            };
            return query;
        },
        processResults: function (data) {
          return {
            results: data
          };
        },
        cache: true
      }
    });
  });




// Document ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Reset modal when it's hidden
    document.getElementById('modalVenda').addEventListener('hidden.bs.modal', function () {
        resetModal();
    });

    // Form validation
    document.getElementById('formVenda').addEventListener('submit', function(e) {
        if (!validateForm()) {
            e.preventDefault();
        }
    });

    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card, .stats-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
});

// Reset modal to add mode
function resetModal() {
    editingId = null;
    document.getElementById('modalTitle').textContent = 'Nova Venda';
    document.getElementById('formVenda').action = '/adicionar_venda';
    document.getElementById('formVenda').reset();
    
    // Remove any error styling
    const inputs = document.querySelectorAll('#formVenda .form-control, #formVenda .form-select');
    inputs.forEach(input => {
        input.classList.remove('is-invalid');
    });
}

// Edit sale function
function editarVenda(id) {
    editingId = id;
    
    // Change modal title and form action
    document.getElementById('modalTitle').textContent = 'Editar Venda';
    document.getElementById('formVenda').action = `/editar_venda/${id}`;
    
    // Fetch sale data
    fetch(`/obter_venda/${id}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao buscar dados da venda');
            }
            return response.json();
        })
        .then(data => {
            // Populate form fields
            document.getElementById('nome_produto').value = data.nome_produto;
            document.getElementById('nome_vendedor').value = data.nome_vendedor;
            document.getElementById('nome_comprador').value = data.nome_comprador;
            document.getElementById('grupo_comprador').value = data.grupo_comprador;
            document.getElementById('quantidade').value = data.quantidade;
            document.getElementById('preco_unitario').value = data.preco_unitario;
            document.getElementById('status_pagamento').checked = data.status_pagamento;
            
            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('modalVenda'));
            modal.show();
        })
        .catch(error => {
            console.error('Erro:', error);
            showAlert('Erro ao carregar dados da venda: ' + error.message, 'danger');
        });
}

// Confirm deletion
function confirmarExclusao(id) {
    if (confirm('Tem certeza que deseja excluir esta venda? Esta ação não pode ser desfeita.')) {
        // Create and submit deletion form
        const form = document.getElementById('formExcluir');
        form.action = `/excluir_venda/${id}`;
        form.submit();
    }
}

// Form validation
function validateForm() {
    let isValid = true;
    const requiredFields = [
        'nome_produto',
        'nome_vendedor', 
        'nome_comprador',
        'grupo_comprador',
        'quantidade',
        'preco_unitario'
    ];
    
    requiredFields.forEach(fieldName => {
        const field = document.getElementById(fieldName);
        const value = field.value.trim();
        
        // Remove previous error styling
        field.classList.remove('is-invalid');
        
        // Check if field is empty
        if (!value) {
            field.classList.add('is-invalid');
            isValid = false;
        }
        
        // Additional validations
        if (fieldName === 'quantidade' && value && parseInt(value) < 1) {
            field.classList.add('is-invalid');
            isValid = false;
        }
        
        if (fieldName === 'preco_unitario' && value && parseFloat(value) < 0) {
            field.classList.add('is-invalid');
            isValid = false;
        }
    });
    
    if (!isValid) {
        showAlert('Por favor, preencha todos os campos obrigatórios corretamente.', 'danger');
    }
    
    return isValid;
}

// Show alert function
function showAlert(message, type = 'info') {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert-custom');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create new alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show alert-custom`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert alert at the top of main content
    const main = document.querySelector('main');
    main.insertBefore(alertDiv, main.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Real-time search functionality (optional enhancement)
function setupRealtimeSearch() {
    const searchInputs = ['vendedor', 'comprador', 'id'];
    let searchTimeout;
    
    searchInputs.forEach(inputName => {
        const input = document.getElementById(inputName);
        if (input) {
            input.addEventListener('input', function() {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    // Auto-submit form after user stops typing for 500ms
                    if (this.value.length >= 2 || this.value.length === 0) {
                        this.form.submit();
                    }
                }, 500);
            });
        }
    });
}

// Calculate total value in real-time
function setupValueCalculation() {
    const quantidadeInput = document.getElementById('quantidade');
    const precoInput = document.getElementById('preco_unitario');
    
    function updateTotal() {
        const quantidade = parseInt(quantidadeInput.value) || 0;
        const preco = parseFloat(precoInput.value) || 0;
        const total = quantidade * preco;
        
        // You could display this total somewhere in the modal
        // For now, we'll just log it
        console.log('Total calculado:', total.toFixed(2));
    }
    
    if (quantidadeInput && precoInput) {
        quantidadeInput.addEventListener('input', updateTotal);
        precoInput.addEventListener('input', updateTotal);
    }
}

// Initialize additional features
document.addEventListener('DOMContentLoaded', function() {
    setupValueCalculation();
    // setupRealtimeSearch(); // Uncomment if you want real-time search
});

// Export confirmation
function confirmarExportacao() {
    return confirm('Deseja exportar todos os dados para Excel?');
}

// Utility function to format currency
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

// Utility function to format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Print functionality
function printTable() {
    window.print();
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + N for new sale
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        const modal = new bootstrap.Modal(document.getElementById('modalVenda'));
        modal.show();
    }
    
    // Escape to close modal
    if (e.key === 'Escape') {
        const modal = bootstrap.Modal.getInstance(document.getElementById('modalVenda'));
        if (modal) {
            modal.hide();
        }
    }
});

// Service Worker registration for PWA capabilities (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // Could register a service worker here for offline capabilities
        console.log('PWA capabilities available');
    });
}


$(document).ready(function () {
            const precoPorUnidade = 20;

            $('#quantidade').on('input', function () {
                const quantidade = parseInt($(this).val()) || 0;
                const precoTotal = quantidade * precoPorUnidade;
                $('#preco_unitario').val(precoTotal.toFixed(2));
            });
        });