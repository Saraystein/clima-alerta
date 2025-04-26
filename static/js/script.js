// --- Autocomplete com Geoapify ---
const citySearch = document.getElementById("citySearch");
const suggestionBox = document.getElementById("suggestions");

citySearch.addEventListener("input", async () => {
  const query = citySearch.value.trim();
  if (query.length < 2) {
    suggestionBox.innerHTML = "";
    return;
  }

  try {
    const res = await fetch(
      `https://api.geoapify.com/v1/geocode/autocomplete?text=${query}&limit=5&lang=pt&apiKey=fb019c1d1d18980deecce5e1e860f545`
    );
    const data = await res.json();
    suggestionBox.innerHTML = "";

    data.features.forEach((place) => {
      const li = document.createElement("li");
      li.textContent =
        place.properties.city ||
        place.properties.name ||
        place.properties.formatted;
      li.addEventListener("click", () => {
        citySearch.value = li.textContent;
        suggestionBox.innerHTML = "";
      });
      suggestionBox.appendChild(li);
    });
  } catch (error) {
    console.error("Erro nas sugestões:", error);
  }
});

// --- Gráfico Clima com Chart.js ---
if (typeof window.dadosPrevisao !== "undefined") {
  const ctx = document.getElementById("graficoClima");

  const horarios = window.dadosPrevisao.map((item) =>
    item.dt_txt.split(" ")[1].slice(0, 5)
  );
  const temperaturas = window.dadosPrevisao.map((item) => item.main.temp);

  new Chart(ctx, {
    type: "line",
    data: {
      labels: horarios,
      datasets: [
        {
          label: "Temperatura (°C)",
          data: temperaturas,
          borderColor: "#0d6efd",
          backgroundColor: "rgba(13, 110, 253, 0.2)",
          fill: true,
          tension: 0.4,
          pointRadius: 3,
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: false,
          title: {
            display: true,
            text: "°C",
          },
        },
      },
    },
  });
}
