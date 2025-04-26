document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("citySearch");
    const suggestionsBox = document.getElementById("suggestions");
  
    input.addEventListener("input", async () => {
      const query = input.value.trim();
      if (query.length < 2) {
        suggestionsBox.innerHTML = "";
        return;
      }
  
      try {
        const response = await fetch(`https://wft-geo-db.p.rapidapi.com/v1/geo/cities?limit=5&namePrefix=${query}`, {
          method: "GET",
          headers: {
            "X-RapidAPI-Key": "abfc30899emsh7ba68e8d3365046p1f2037jsn65d23ee19ab9",  // Substitua pela sua se necessário
            "X-RapidAPI-Host": "wft-geo-db.p.rapidapi.com"
          }
        });
  
        const data = await response.json();
        const cities = data.data;
  
        suggestionsBox.innerHTML = "";
  
        cities.forEach(city => {
          const li = document.createElement("li");
          li.classList.add("suggestion-item");
          li.textContent = `${city.city}, ${city.countryCode}`;
          li.addEventListener("click", () => {
            input.value = `${city.city}, ${city.countryCode}`;
            suggestionsBox.innerHTML = "";
          });
          suggestionsBox.appendChild(li);
        });
  
      } catch (error) {
        console.error("Erro ao buscar sugestões:", error);
      }
    });
  
    document.addEventListener("click", (e) => {
      if (!suggestionsBox.contains(e.target) && e.target !== input) {
        suggestionsBox.innerHTML = "";
      }
    });
  });
  