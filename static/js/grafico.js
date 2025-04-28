document.addEventListener('DOMContentLoaded', function() {
  const ctx = document.getElementById('graficoClima').getContext('2d');
  const horarios = window.dadosPrevisao.slice(0, 8).map(item => item.dt_txt.split(' ')[1].substring(0,5));
  const temperaturas = window.dadosPrevisao.slice(0, 8).map(item => item.main.temp);

  window.graficoClima = new Chart(ctx, {
    type: 'line',
    data: {
      labels: horarios,
      datasets: [{
        label: 'Temp (°C)',
        data: temperaturas,
        backgroundColor: 'rgba(13, 110, 253, 0.2)',
        borderColor: 'rgba(13, 110, 253, 1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: false
        }
      }
    }
  });
});
