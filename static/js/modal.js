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












// Variables de modal
var modal = document.getElementById("myModal");

// Variables de formulario
var formAgregar = document.getElementById('formCosto');
var precioInput = document.getElementById('precio');
var tipoHabitacionInput = document.getElementById('tipo_habitacion');

// Mostrar el modal de "Agregar"
document.getElementById('openModalBtn').addEventListener('click', function() {
    // Resetear formulario y mostrar el modal
    formAgregar.reset();
    modal.style.display = 'block';
    formAgregar.dataset.action = 'add';  // Acción 'add' cuando se agrega
    formAgregar.dataset.id = '';  // Limpiar cualquier ID previamente almacenado
});

// Cerrar el modal al hacer clic en la "X"
document.querySelector('#myModal .close').addEventListener('click', function() {
    modal.style.display = 'none';
});

// Función para abrir el modal de "Editar" con los datos cargados
async function abrirModalEditar(id) {
    try {
        const response = await fetch(`/api/datos/${id}`);
        if (!response.ok) {
            throw new Error('Error al obtener los datos del costo');
        }

        const costo = await response.json();

        // Cargar los datos en los campos del formulario
        precioInput.value = costo.precio;
        tipoHabitacionInput.value = costo.tipo_habitacion;

        // Establecer los datos del formulario para editar
        formAgregar.dataset.action = 'edit';  // Acción 'edit' cuando se edita
        formAgregar.dataset.id = id;  // Guardar el ID para la edición

        modal.style.display = 'block';  // Mostrar el modal
    } catch (err) {
        Swal.fire('Error', 'Hubo un problema al cargar los datos para editar', 'error');
        console.error('Error al cargar datos:', err);
    }
}

// Manejo del formulario de agregar y editar
formAgregar.addEventListener('submit', async function(e) {
    e.preventDefault();

    const action = formAgregar.dataset.action;  // Obtener la acción (add o edit)
    const id = formAgregar.dataset.id;  // Obtener el ID si es edición
    const precio = precioInput.value;
    const tipoHabitacion = tipoHabitacionInput.value;

    const data = {
        precio: precio,
        tipo_habitacion: tipoHabitacion,
        estatus: 'activo'
    };

    try {
        let response;

        if (action === 'add') {
            // Si es agregar
            response = await fetch('/api/datos', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
        } else if (action === 'edit') {
            // Si es editar
            response = await fetch(`/api/datos/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
        }

        if (response.ok) {
            Swal.fire('Éxito', action === 'add' ? 'Costo agregado correctamente' : 'Costo actualizado correctamente', 'success');
            modal.style.display = 'none';  // Cerrar el modal
            cargarCostos();  // Recargar la lista de costos
        } else {
            const error = await response.json();
            Swal.fire('Error', error.mensaje || 'Error al procesar el costo', 'error');
        }
    } catch (err) {
        Swal.fire('Error', 'Hubo un problema al procesar la solicitud', 'error');
        console.error('Error al realizar la solicitud:', err);
    }
});

// Función para cargar los costos
async function cargarCostos() {
    try {
        const response = await fetch('/api/datos');
        const costos = await response.json();

        const tbody = document.getElementById('costosBody');
        tbody.innerHTML = '';  // Limpiar la tabla antes de agregar nuevos datos

        costos.forEach(costo => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${costo.ID_Costo}</td>
                <td>${costo.precio}</td>
                <td>${costo.tipo_habitacion}</td>
                <td>
                    <button class="btn btn-sm btn-warning" onclick="abrirModalEditar(${costo.ID_Costo})">Editar</button>
                    <button class="btn btn-sm btn-danger" onclick="eliminarCosto(${costo.ID_Costo})">Eliminar</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (err) {
        console.error('Error al cargar los costos:', err);
    }
}

// Llamar a cargarCostos cuando se carga la página
window.onload = cargarCostos;

// Función para eliminar un costo
async function eliminarCosto(id) {
    const confirm = await Swal.fire({
        title: '¿Estás seguro?',
        text: 'Esta acción no se puede deshacer.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar',
    });

    if (confirm.isConfirmed) {
        try {
            const response = await fetch(`/api/costos/${id}`, { method: 'DELETE' });

            if (response.ok) {
                Swal.fire('¡Eliminado!', 'El costo ha sido eliminado', 'success');
                cargarCostos();  // Recargar la lista de costos
            } else {
                const error = await response.json();
                Swal.fire('Error', error.error || 'No se pudo eliminar el costo', 'error');
            }
        } catch (err) {
            Swal.fire('Error', 'Hubo un problema al eliminar el costo', 'error');
        }
    }
}
