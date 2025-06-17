// Global variables
let editingId = null;

$(document).ready(function () {
    // Armazena a instância da tabela em uma variável
    var table = $('#vendasTable').DataTable({
        searching: false,
        lengthChange: false,
        responsive: true,
        pagingType: "simple_numbers",
        order: [[9, 'desc']],

        ajax: {
            url: '/api/vendas',
            data: function (d) {
                d.vendedor = $('#vendedor').val();
                d.comprador = $('#comprador').val();
                d.id = $('#id').val();
                d.status_pagamento = $('#status_pagamento').val(); 
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
                render: function (data) {
                    if (data === 'M') return '<span class="badge bg-success">Meninos</span>';
                    else if (data === 'F') return '<span class="badge bg-danger">Meninas</span>';
                    else return '<span class="badge bg-warning">Igreja</span>';
                }
            },
            { data: 'quantidade' },
            { data: 'preco_unitario' },
            { data: 'valor_total' },
            {
                data: 'status_pagamento',
                render: function (data) {
                    if (data === 'Pago')
                        return '<span class="badge bg-success">Pago</span>';
                    else
                        return '<span class="badge bg-danger">Pendente</span>';
                }
            },
            {
                data: 'entrega_status',
                render: function (data) {
                    if (data === 'Entregue')
                        return '<span class="badge bg-success">Entregue</span>';
                    else
                        return '<span class="badge bg-danger">Pendente</span>';
                }
            },
            { data: 'data_venda' },
            {
                data: 'id',
                orderable: false,
                render: function (id) {
                    return `
                        <div class="btn-group" role="group">
                            <button type="button" class="btn btn-sm btn-warning" onclick="editarVenda('${id}')" title="Editar">
                                <i class="fas fa-edit"></i>
                            </button>

                            <button type="button" class="btn btn-sm btn-danger" onclick="EntregaPedido('${id}')" title="Entregar Pedido">
                                <i class="fas fa-share-square"></i>
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
    $('#btnFiltrar').on('click', function () {
        table.ajax.reload();
    });

    // Botão "Limpar"
    $('#btnLimpar').on('click', function () {
        $('#filtrosForm')[0].reset();
        table.ajax.reload();
    });
});


$(document).ready(function () {
    $('#filter_vendedor').select2({
        theme: "bootstrap-5",
        width: $("#filter_vendedor").data("width")
            ? $("#filter_vendedor").data("width")
            : $("#filter_vendedor").hasClass("w-100")
                ? "100%"
                : "style",
        placeholder: $("#filter_vendedor").data('placeholder'),
        closeOnSelect: false,
        maximumSelectionLength: 3,
        ajax: {
            url: '/api/filter_vendedor',
            dataType: 'json',
            delay: 250,
            data: function (params) {
                var query = {
                    serch: params.term,
                    type: "internal"
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
document.addEventListener('DOMContentLoaded', function () {
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
    document.getElementById('formVenda').addEventListener('submit', function (e) {
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


function EntregaPedido(id) {
    // Armazena o ID do pedido para envio posterior
    document.getElementById('pedido_id').value = id;

    // Requisição dos dados da venda
    fetch(`/obter_venda/${id}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao buscar dados da venda');
            }
            return response.json();
        })
        .then(data => {
            // Preencher os campos do modal de entrega
            document.getElementById('entrega_vendedor').value = data.nome_vendedor;
            document.getElementById('entrega_comprador').value = data.nome_comprador;
            document.getElementById('entrega_quantidade').value = data.quantidade;

            // Formatar o valor como moeda brasileira
            const valorTotal = (data.quantidade * data.preco_unitario).toLocaleString('pt-BR', {
                style: 'currency',
                currency: 'BRL'
            });
            document.getElementById('entrega_valor').value = valorTotal;

            // Resetar campos selecionáveis
            document.getElementById('entregador').value = "";
            document.getElementById('confirmar_entrega').checked = false;

            // Mostrar o modal de entrega
            const modal = new bootstrap.Modal(document.getElementById('modalEntrega'));
            modal.show();
        })
        .catch(error => {
            console.error('Erro:', error);
            showAlert('Erro ao carregar dados da venda: ' + error.message, 'danger');
        });
}



// Confirm deletion
function confirmarExclusao(id) {
    Swal.fire({
        title: 'Tem certeza?',
        text: 'Essa ação não pode ser desfeita!',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sim, excluir',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#d33',
        cancelButtonColor: '#6c757d'
    }).then((result) => {
        if (result.isConfirmed) {
            // Submete o formulário de exclusão
            const form = document.getElementById('formExcluir');
            form.action = `/excluir_venda/${id}`;
            form.submit();
        }
    });
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
            input.addEventListener('input', function () {
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
document.addEventListener('DOMContentLoaded', function () {
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
document.addEventListener('keydown', function (e) {
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
    window.addEventListener('load', function () {
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


$(document).ready(function () {
    const $collapse = $('#filtrosCollapse');
    const $icon = $('#iconeSeta');

    $collapse.on('show.bs.collapse', function () {
        $icon.removeClass('fa-chevron-down').addClass('fa-chevron-up');
    });

    $collapse.on('hide.bs.collapse', function () {
        $icon.removeClass('fa-chevron-up').addClass('fa-chevron-down');
    });

    // --- Coloque o código JavaScript para os gráficos aqui ---
    // Você precisará carregar a biblioteca Chart.js primeiro no seu base.html ou neste arquivo.
    // Exemplo de como incluir Chart.js (geralmente no head ou antes do seu script principal):
    // <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    // Exemplo de como buscar dados e renderizar os gráficos (ajuste os endpoints do Flask):
    async function fetchDataForCharts() {
        // Exemplo: buscar dados de vendas por grupo
        const groupSalesResponse = await fetch('/api/sales_by_group');
        const groupSalesData = await groupSalesResponse.json();

        // Exemplo: buscar dados de status de pagamento
        const paymentStatusResponse = await fetch('/api/payment_status');
        const paymentStatusData = await paymentStatusResponse.json();

        // Exemplo: buscar dados de vendas diárias
        const dailySalesResponse = await fetch('/api/daily_sales');
        const dailySalesData = await dailySalesResponse.json();

        // Renderizar gráfico de Vendas por Grupo
        if (document.getElementById('vendasPorGrupoChart')) {
            const ctxGroup = document.getElementById('vendasPorGrupoChart').getContext('2d');
            new Chart(ctxGroup, {
                type: 'pie', // Ou 'doughnut'
                data: {
                    labels: groupSalesData.labels, // Ex: ['Meninos', 'Meninas', 'Igreja']
                    datasets: [{
                        data: groupSalesData.values, // Ex: [26, 105, 45]
                        backgroundColor: [
                            'rgba(54, 162, 235, 0.7)', // Azul para Meninos
                            'rgba(255, 99, 132, 0.7)', // Vermelho para Meninas
                            'rgba(255, 205, 86, 0.7)'  // Amarelo para Igreja
                        ],
                        borderColor: [
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 99, 132, 1)',
                            'rgba(255, 205, 86, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false, // Importante para ajustar ao tamanho da div
                    plugins: {
                        legend: {
                            position: 'right',
                        },
                        title: {
                            display: false, // Título já no card-header
                        }
                    }
                }
            });
        }

        // Renderizar gráfico de Status de Pagamento
        if (document.getElementById('statusPagamentoChart')) {
            const ctxPayment = document.getElementById('statusPagamentoChart').getContext('2d');
            new Chart(ctxPayment, {
                type: 'bar',
                data: {
                    labels: paymentStatusData.labels, // Ex: ['Pago', 'Não Pago']
                    datasets: [{
                        label: 'Quantidade de Vendas',
                        data: paymentStatusData.values, // Ex: [90, 86]
                        backgroundColor: [
                            'rgba(75, 192, 192, 0.7)', // Verde para Pago
                            'rgba(255, 99, 132, 0.7)'  // Vermelho para Não Pago
                        ],
                        borderColor: [
                            'rgba(75, 192, 192, 1)',
                            'rgba(255, 99, 132, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false,
                        },
                        title: {
                            display: false,
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                precision: 0 // Garante que os rótulos do eixo Y sejam inteiros
                            }
                        }
                    }
                }
            });
        }

        // Renderizar gráfico de Vendas Diárias (exemplo de gráfico de linha)
        if (document.getElementById('vendasDiariasChart')) {
            const ctxDaily = document.getElementById('vendasDiariasChart').getContext('2d');
            new Chart(ctxDaily, {
                type: 'line',
                data: {
                    labels: dailySalesData.labels, // Ex: ['10/06', '11/06', '12/06', '13/06', '14/06']
                    datasets: [{
                        label: 'Vendas (R$)',
                        data: dailySalesData.values, // Ex: [150, 200, 180, 250, 220]
                        fill: false,
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false,
                        },
                        title: {
                            display: false,
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
    }

    // Chame a função para buscar e renderizar os gráficos quando o DOM estiver pronto
    fetchDataForCharts();

});

$(document).ready(function() {
  function toggleConfirmarEntrega() {
    const acao = $('#acao_entrega').val();
    if (acao === 'confirmar') {
      $('#checkConfirmarEntrega').show();
      $('#confirmar_entrega').prop('required', true);
    } else {
      $('#checkConfirmarEntrega').hide();
      $('#confirmar_entrega').prop('required', false).prop('checked', false);
    }
  }

  // Inicializa o estado no carregamento da página
  toggleConfirmarEntrega();

  // Atualiza quando o select mudar
  $('#acao_entrega').on('change', function() {
    toggleConfirmarEntrega();
  });
});


$(document).ready(function () {
    $('#formEntrega').on('submit', function (e) {
        e.preventDefault(); // Impede o envio padrão do formulário

        var formData = new FormData(this);

        $.ajax({
            url: '/entregar_pedido',
            type: 'POST',
            data: formData,
            processData: false, // não processa os dados
            contentType: false, // não define content-type

            success: function (response) {
                Swal.fire({
                    icon: 'success',
                    title: 'Entrega registrada!',
                    text: 'O status foi atualizado com sucesso.',
                    confirmButtonColor: '#28a745'
                }).then(() => {
                    // Fecha o modal
                    var modalElement = document.getElementById('modalEntrega');
                    var modal = bootstrap.Modal.getInstance(modalElement);
                    if (modal) {
                        modal.hide();
                    }

                    // Recarrega a DataTable (ajuste o ID se necessário)
                    $('#vendasTable').DataTable().ajax.reload();
                });
            },

            error: function (xhr, status, error) {
                let errorMsg = 'Ocorreu um erro ao registrar a entrega.';
                if (xhr.responseJSON && xhr.responseJSON.erro) {
                    errorMsg = xhr.responseJSON.erro;
                }

                Swal.fire({
                    icon: 'error',
                    title: 'Erro!',
                    text: errorMsg,
                    confirmButtonColor: '#dc3545'
                });
            }
        });
    });
});
