// Obtener el modal
var modal = document.getElementById("myModal");

// Obtener el botón que abre el modal
var btn = document.getElementById("openModalBtn");

// Obtener el elemento <span> que cierra el modal
var span = document.getElementsByClassName("close")[0];

// Cuando el usuario hace clic en el botón, abre el modal
btn.onclick = function() {
  modal.style.display = "block";
}

// Cuando el usuario hace clic en <span> (x), cierra el modal
span.onclick = function() {
  modal.style.display = "none";
}

// Cuando el usuario hace clic fuera del modal, también lo cierra
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("formCosto");
  const modal = document.getElementById("myModal");
  const closeModal = document.querySelector(".close");

  // Función para cerrar el modal
  closeModal.onclick = () => (modal.style.display = "none");

  // Enviar datos a la API
  form.onsubmit = async (event) => {
      event.preventDefault();

      const precio = document.getElementById("precio").value;
      const tipo_habitacion = document.getElementById("tipo_habitacion").value;

      try {
          const response = await fetch("/api/datos", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                  precio,
                  tipo_habitacion,
                  estatus: "activo",
              }),
          });

          if (response.ok) {
              alert("Costo agregado correctamente");
              form.reset(); // Limpiar formulario
              modal.style.display = "none"; // Cerrar modal
              cargarCostos(); // Recargar lista
          } else {
              const error = await response.json();
              alert(`Error: ${error.mensaje || "Error al agregar el costo"}`);
          }
      } catch (err) {
          console.error("Error al enviar los datos", err);
      }
  };

  // Cargar lista de costos
  async function cargarCostos() {
      try {
          const response = await fetch("/api/datos");
          const data = await response.json();

          const tbody = document.querySelector("table tbody");
          tbody.innerHTML = ""; // Limpiar la tabla

          data.forEach((costo, index) => {
              tbody.innerHTML += `
                  <tr>
                      <td>${index + 1}</td>
                      <td>${costo.precio}</td>
                      <td>${costo.tipo_habitacion}</td>
                      <td>
                          <button class="btn btn-sm btn-warning" onclick="editarCosto(${costo.id_costo})">Editar</button>
                          <button class="btn btn-sm btn-danger" onclick="eliminarCosto(${costo.id_costo})">Eliminar</button>
                      </td>
                  </tr>
              `;
          });
      } catch (err) {
          console.error("Error al cargar los costos", err);
      }
  }

  // Llamar a cargarCostos al cargar la página
  cargarCostos();
});



async function editarCosto(id) {
  const nuevoPrecio = prompt("Ingrese el nuevo precio:");
  const nuevoTipo = prompt("Ingrese el nuevo tipo de habitación:");

  if (nuevoPrecio && nuevoTipo) {
      try {
          const response = await fetch(`/api/datos/${id}`, {
              method: "PUT",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                  precio: nuevoPrecio,
                  tipo_habitacion: nuevoTipo,
                  estatus: "activo",
              }),
          });

          if (response.ok) {
              alert("Costo actualizado correctamente");
              cargarCostos();
          } else {
              const error = await response.json();
              alert(`Error: ${error.mensaje || "Error al actualizar el costo"}`);
          }
      } catch (err) {
          console.error("Error al actualizar el costo", err);
      }
  }
}

async function eliminarCosto(id) {
  if (confirm("¿Estás seguro de que deseas eliminar este costo?")) {
      try {
          const response = await fetch(`/api/datos/${id}`, {
              method: "DELETE",
          });

          if (response.ok) {
              alert("Costo eliminado correctamente");
              cargarCostos();
          } else {
              const error = await response.json();
              alert(`Error: ${error.error || "Error al eliminar el costo"}`);
          }
      } catch (err) {
          console.error("Error al eliminar el costo", err);
      }
  }
}



