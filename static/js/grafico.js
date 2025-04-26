window.onload = () => {
  const canvas = document.getElementById("graficoClima");
  const previsao = window.dadosPrevisao || [];

  if (!canvas || !previsao.length) return;

  const ctx = canvas.getContext("2d");

  const horarios = previsao.map(item => item.dt_txt.split(" ")[1].slice(0, 5));
  const temperaturas = previsao.map(item => item.main.temp);

  const gradient = ctx.createLinearGradient(0, 0, 0, 400);
  gradient.addColorStop(0, "#ff5722");
  gradient.addColorStop(1, "#2196f3");

  new Chart(ctx, {
    type: "line",
    data: {
      labels: horarios,
      datasets: [{
        label: "Temperatura (°C)",
        data: temperaturas,
        borderColor: "#ff5722",
        backgroundColor: gradient,
        fill: true,
        tension: 0.4,
        pointRadius: 5,
        pointHoverRadius: 6
      }]
    },
    options: {
      responsive: true,
      animation: {
        duration: 1000,
        easing: "easeOutQuart"
      },
      plugins: {
        legend: { labels: { font: { size: 14 } } },
        tooltip: {
          callbacks: {
            label: context => `${context.parsed.y} °C`
          }
        }
      },
      scales: {
        y: {
          title: { display: true, text: "Temperatura (°C)" }
        },
        x: {
          title: { display: true, text: "Horário" }
        }
      }
    }
  });
};
