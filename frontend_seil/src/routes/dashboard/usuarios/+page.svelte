<script lang="ts">
    import { enhance } from '$app/forms';
    import type { ActionData, PageData } from './$types';
    import type { UserListItem } from '$lib/types/api';

    let { data, form }: { data: PageData, form: ActionData } = $props();

    // Sincronizar usuarios locales con los datos del servidor para filtrado reactivo
    let usuariosRaw = $derived(data.users || []);
    
    // Mapear el formato de la API al formato esperado por la UI si es necesario
    let usuarios = $derived(usuariosRaw.map(u => ({
        id: u.id,
        nombre: u.name || u.username,
        email: u.email,
        rol: u.role === 'ADMIN' ? 'Administrador' : u.role === 'GERENCIA' ? 'Gerente' : 'Analista',
        ultimoAcceso: u.last_login_at ? new Date(u.last_login_at).toLocaleString() : 'Nunca',
        estado: u.is_active ? 'Activo' : 'Inactivo',
        fechaCreacion: 'N/A', // La API no parece retornar esto en UserListItem
        area: u.department || 'N/A',
        username: u.username
    })));

    // Estados para modales y formularios
    let mostrarModalNuevo = $state(false);
    let mostrarModalEditar = $state(false);
    let mostrarModalEliminar = $state(false);
    let usuarioSeleccionado = $state<any>(null);
    let filtroRol = $state('todos');
    let filtroEstado = $state('todos');
    let filtroBusqueda = $state('');
    let isLoading = $state(false);
  
    // Roles permitidos según el documento
    const roles = ['Administrador', 'Analista', 'Operador', 'Gerente', 'Visualizador'];
    const estados = ['Activo', 'Inactivo', 'Pendiente'];
  
    // Funciones
    function abrirModalNuevo() {
      mostrarModalNuevo = true;
    }
  
    function abrirModalEditar(usuario: any) {
      usuarioSeleccionado = { ...usuario };
      mostrarModalEditar = true;
    }
  
    function abrirModalEliminar(usuario: any) {
      usuarioSeleccionado = usuario;
      mostrarModalEliminar = true;
    }
  
    // Filtrar usuarios
    let usuariosFiltrados = $derived(usuarios.filter(usuario => {
      const cumpleRol = filtroRol === 'todos' || usuario.rol === filtroRol;
      const cumpleEstado = filtroEstado === 'todos' || usuario.estado === filtroEstado;
      const cumpleBusqueda = filtroBusqueda === '' || 
        usuario.nombre.toLowerCase().includes(filtroBusqueda.toLowerCase()) ||
        usuario.email.toLowerCase().includes(filtroBusqueda.toLowerCase()) ||
        (usuario.area?.toLowerCase().includes(filtroBusqueda.toLowerCase()) || false);
      
      return cumpleRol && cumpleEstado && cumpleBusqueda;
    }));
  
    // Obtener color según rol
    function getRolColor(rol: string) {
      switch(rol) {
        case 'Administrador': return 'bg-red-900/30 text-red-400 border border-red-600/20';
        case 'Analista': return 'bg-blue-900/30 text-blue-400 border border-blue-600/20';
        case 'Operador': return 'bg-green-900/30 text-green-400 border border-green-600/20';
        case 'Gerente': return 'bg-purple-900/30 text-purple-400 border border-purple-600/20';
        case 'Visualizador': return 'bg-yellow-900/30 text-yellow-400 border border-yellow-600/20';
        default: return 'bg-gray-900/30 text-gray-400 border border-gray-600/20';
      }
    }
  
    // Obtener color según estado
    function getEstadoColor(estado: string) {
      switch(estado) {
        case 'Activo': return 'text-green-400 bg-green-900/20';
        case 'Inactivo': return 'text-red-400 bg-red-900/20';
        case 'Pendiente': return 'text-yellow-400 bg-yellow-900/20';
        default: return 'text-gray-400 bg-gray-900/20';
      }
    }
</script>
  
  <div class="min-h-full p-6">
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-white mb-2">Gestión de Usuarios</h1>
          <p class="text-gray-400">
            Administración de accesos, roles y permisos del sistema - Control AAA (Autenticación, Autorización, Auditoría)
          </p>
        </div>
        <button 
          onclick={abrirModalNuevo}
          class="px-6 py-3 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white rounded-xl font-medium flex items-center transition-all shadow-lg hover:shadow-xl hover:-translate-y-0.5"
          aria-label="Agregar nuevo usuario"
          title="Crear nuevo usuario"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Nuevo Usuario
        </button>
      </div>
    </div>
  
    <!-- Panel de estadísticas -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <div class="bg-gradient-to-br from-gray-900/80 to-gray-800/80 rounded-2xl border border-gray-700 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-400 text-sm">Total Usuarios</p>
            <p class="text-3xl font-bold text-white mt-1">{data.stats?.total_users ?? usuarios.length}</p>
          </div>
          <div class="h-12 w-12 bg-gradient-to-br from-red-600/20 to-red-700/20 rounded-xl flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </div>
        </div>
      </div>
  
      <div class="bg-gradient-to-br from-gray-900/80 to-gray-800/80 rounded-2xl border border-gray-700 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-400 text-sm">Activos</p>
            <p class="text-3xl font-bold text-white mt-1">
              {data.stats?.active_users ?? usuarios.filter(u => u.estado === 'Activo').length}
            </p>
          </div>
          <div class="h-12 w-12 bg-gradient-to-br from-green-600/20 to-green-700/20 rounded-xl flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
      </div>
  
      <div class="bg-gradient-to-br from-gray-900/80 to-gray-800/80 rounded-2xl border border-gray-700 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-400 text-sm">Administradores</p>
            <p class="text-3xl font-bold text-white mt-1">
              {data.stats?.admin_users ?? usuarios.filter(u => u.rol === 'Administrador').length}
            </p>
          </div>
          <div class="h-12 w-12 bg-gradient-to-br from-red-600/20 to-red-700/20 rounded-xl flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
        </div>
      </div>
  
      <div class="bg-gradient-to-br from-gray-900/80 to-gray-800/80 rounded-2xl border border-gray-700 p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-400 text-sm">Último acceso</p>
            <p class="text-xl font-bold text-white mt-1">
              {data.stats?.last_access ? new Date(data.stats.last_access).toLocaleDateString() : 'N/A'}
            </p>
          </div>
          <div class="h-12 w-12 bg-gradient-to-br from-blue-600/20 to-blue-700/20 rounded-xl flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    {#if data.error || form?.message}
        <div class="mb-6 p-4 rounded-xl bg-red-900/30 border border-red-700/50 text-red-400">
            {data.error || form?.message}
        </div>
    {/if}
    {#if form?.success}
        <div class="mb-6 p-4 rounded-xl bg-green-900/30 border border-green-700/50 text-green-400">
            {form.message}
        </div>
    {/if}
  
    <!-- Filtros -->
    <div class="bg-gradient-to-br from-gray-900/80 to-gray-800/80 rounded-2xl border border-gray-700 p-6 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label for="busqueda" class="block text-sm font-medium text-gray-300 mb-2">Buscar usuario</label>
          <div class="relative">
            <input
              id="busqueda"
              type="text"
              bind:value={filtroBusqueda}
              placeholder="Nombre, email o área..."
              class="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
              aria-label="Buscar usuarios"
            />
            <svg class="absolute right-3 top-3 h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
  
        <div>
          <label for="filtroRol" class="block text-sm font-medium text-gray-300 mb-2">Filtrar por rol</label>
          <select 
            id="filtroRol"
            bind:value={filtroRol}
            class="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
            aria-label="Filtrar por rol de usuario"
          >
            <option value="todos">Todos los roles</option>
            {#each roles as rol}
              <option value={rol}>{rol}</option>
            {/each}
          </select>
        </div>
  
        <div>
          <label for="filtroEstado" class="block text-sm font-medium text-gray-300 mb-2">Filtrar por estado</label>
          <select 
            id="filtroEstado"
            bind:value={filtroEstado}
            class="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
            aria-label="Filtrar por estado de usuario"
          >
            <option value="todos">Todos los estados</option>
            {#each estados as estado}
              <option value={estado}>{estado}</option>
            {/each}
          </select>
        </div>
      </div>
    </div>
  
    <!-- Tabla de usuarios -->
    <div class="bg-gradient-to-br from-gray-900/80 to-gray-800/80 rounded-2xl border border-gray-700 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-gray-700 bg-gradient-to-r from-gray-900 to-gray-800">
              <th class="py-4 px-6 text-left text-sm font-medium text-gray-300">Usuario</th>
              <th class="py-4 px-6 text-left text-sm font-medium text-gray-300">Rol</th>
              <th class="py-4 px-6 text-left text-sm font-medium text-gray-300">Estado</th>
              <th class="py-4 px-6 text-left text-sm font-medium text-gray-300">Último Acceso</th>
              <th class="py-4 px-6 text-left text-sm font-medium text-gray-300">Acciones</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-800">
            {#each usuariosFiltrados as usuario}
              <tr class="hover:bg-gray-800/50 transition-colors">
                <td class="py-4 px-6">
                  <div class="flex items-center">
                    <div class="h-10 w-10 bg-gradient-to-br from-red-600/20 to-red-700/20 rounded-lg flex items-center justify-center mr-3">
                      <span class="text-white font-medium">{usuario.nombre.charAt(0)}</span>
                    </div>
                    <div>
                      <p class="font-medium text-white">{usuario.nombre}</p>
                      <p class="text-sm text-gray-400">{usuario.email}</p>
                      {#if usuario.area}
                        <p class="text-xs text-gray-500 mt-1">{usuario.area}</p>
                      {/if}
                    </div>
                  </div>
                </td>
                <td class="py-4 px-6">
                  <span class={`inline-flex px-3 py-1 rounded-full text-xs font-medium ${getRolColor(usuario.rol)}`}>
                    {usuario.rol}
                  </span>
                </td>
                <td class="py-4 px-6">
                  <span class={`inline-flex px-3 py-1 rounded-full text-xs font-medium ${getEstadoColor(usuario.estado)}`}>
                    {usuario.estado}
                  </span>
                </td>
                <td class="py-4 px-6">
                  <div class="text-sm text-gray-300">{usuario.ultimoAcceso}</div>
                  <div class="text-xs text-gray-500">Creado: {usuario.fechaCreacion}</div>
                </td>
                <td class="py-4 px-6">
                  <div class="flex items-center space-x-2">
                    <button
                      onclick={() => abrirModalEditar(usuario)}
                      class="p-2 text-blue-400 hover:bg-gray-700 rounded-lg transition-colors"
                      aria-label={`Editar usuario ${usuario.nombre}`}
                      title="Editar usuario"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button
                      onclick={() => abrirModalEliminar(usuario)}
                      class="p-2 text-red-400 hover:bg-gray-700 rounded-lg transition-colors"
                      aria-label={`Eliminar usuario ${usuario.nombre}`}
                      title="Eliminar usuario"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                    <button
                      class="p-2 text-green-400 hover:bg-gray-700 rounded-lg transition-colors"
                      aria-label={`Restablecer contraseña de ${usuario.nombre}`}
                      title="Restablecer contraseña"
                    >
                      <svg xmlns="http://www.w3.org2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>
  
    <!-- Pie de página con estadísticas -->
    <div class="mt-6 text-sm text-gray-500">
      <p>
        Mostrando {usuariosFiltrados.length} de {usuarios.length} usuarios • 
        {usuarios.filter(u => u.estado === 'Activo').length} activos • 
        {usuarios.filter(u => u.estado === 'Inactivo').length} inactivos
      </p>
    </div>
  </div>
  
  <!-- Modal Nuevo Usuario -->
  {#if mostrarModalNuevo}
    <div class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div class="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl border border-gray-700 w-full max-w-lg shadow-2xl">
        <div class="p-6 border-b border-gray-700">
          <h2 class="text-xl font-bold text-white">Crear Nuevo Usuario</h2>
          <p class="text-gray-400 text-sm mt-1">Complete los datos del nuevo usuario</p>
        </div>
        
        <form 
            method="POST" 
            action="?/createUser" 
            use:enhance={() => {
                isLoading = true;
                return async ({ result, update }) => {
                    await update();
                    isLoading = false;
                    if (result.type === 'success') {
                        mostrarModalNuevo = false;
                    }
                };
            }}
        >
            <div class="p-6 space-y-4">
                <div>
                    <label for="new_name" class="block text-sm font-medium text-gray-300 mb-2">Nombre completo</label>
                    <input
                        id="new_name"
                        type="text"
                        name="name"
                        required
                        class="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                        placeholder="Ej: Juan Pérez"
                    />
                </div>
                
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label for="new_email" class="block text-sm font-medium text-gray-300 mb-2">Correo electrónico</label>
                        <input
                            id="new_email"
                            type="email"
                            name="email"
                            required
                            class="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                            placeholder="usuario@luckia.cl"
                        />
                    </div>
                    <div>
                        <label for="new_username" class="block text-sm font-medium text-gray-300 mb-2">Nombre de usuario</label>
                        <input
                            id="new_username"
                            type="text"
                            name="username"
                            required
                            class="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                            placeholder="jperez"
                        />
                    </div>
                </div>
                
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label for="new_role" class="block text-sm font-medium text-gray-300 mb-2">Rol</label>
                        <select 
                            id="new_role"
                            name="role"
                            required
                            class="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                        >
                            <option value="ADMIN">ADMIN</option>
                            <option value="GERENCIA">GERENCIA</option>
                            <option value="ANALISTA">ANALISTA</option>
                        </select>
                    </div>
                    <div>
                        <label for="new_department" class="block text-sm font-medium text-gray-300 mb-2">Área (opcional)</label>
                        <input
                            id="new_department"
                            type="text"
                            name="department"
                            class="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                            placeholder="RRHH, IT, etc."
                        />
                    </div>
                </div>
            </div>
            
            <div class="p-6 border-t border-gray-700 flex justify-end space-x-3">
                <button
                    type="button"
                    onclick={() => mostrarModalNuevo = false}
                    class="px-5 py-2.5 bg-gray-800 hover:bg-gray-700 text-white rounded-xl font-medium transition-colors"
                >
                    Cancelar
                </button>
                <button
                    type="submit"
                    disabled={isLoading}
                    class="px-5 py-2.5 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white rounded-xl font-medium transition-colors flex items-center disabled:opacity-50"
                >
                    {#if isLoading}
                        <svg class="animate-spin h-5 w-5 mr-3 text-white" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                        </svg>
                    {/if}
                    Crear Usuario
                </button>
            </div>
        </form>
      </div>
    </div>
  {/if}
  
  <!-- Modal Editar Usuario -->
  {#if mostrarModalEditar && usuarioSeleccionado}
    <div class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div class="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl border border-gray-700 w-full max-w-lg shadow-2xl">
        <div class="p-6 border-b border-gray-700">
          <h2 class="text-xl font-bold text-white">Editar Usuario</h2>
          <p class="text-gray-400 text-sm mt-1">Modificar datos de {usuarioSeleccionado.nombre}</p>
        </div>
        
        <form 
            method="POST" 
            action="?/updateUser" 
            use:enhance={() => {
                isLoading = true;
                return async ({ result, update }) => {
                    await update();
                    isLoading = false;
                    if (result.type === 'success') {
                        mostrarModalEditar = false;
                    }
                };
            }}
        >
            <input type="hidden" name="id" value={usuarioSeleccionado.id} />
            <div class="p-6 space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-300 mb-2">Nombre completo</label>
                <input
                type="text"
                name="name"
                bind:value={usuarioSeleccionado.nombre}
                class="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                aria-label="Nombre del usuario"
                />
            </div>
            
            <div>
                <label class="block text-sm font-medium text-gray-300 mb-2">Correo electrónico</label>
                <input
                type="email"
                name="email"
                bind:value={usuarioSeleccionado.email}
                class="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                aria-label="Email del usuario"
                />
            </div>
            
            <div class="grid grid-cols-2 gap-4">
                <div>
                <label class="block text-sm font-medium text-gray-300 mb-2">Rol</label>
                <select 
                    name="role"
                    bind:value={usuarioSeleccionado.rol}
                    class="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    aria-label="Seleccionar rol del usuario"
                >
                    <option value="Administrador">ADMIN</option>
                    <option value="Gerente">GERENCIA</option>
                    <option value="Analista">ANALISTA</option>
                </select>
                </div>
                
                <div>
                <label class="block text-sm font-medium text-gray-300 mb-2">Estado</label>
                <select 
                    name="is_active"
                    value={usuarioSeleccionado.estado === 'Activo' ? 'true' : 'false'}
                    class="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    aria-label="Seleccionar estado del usuario"
                >
                    <option value="true">Activo</option>
                    <option value="false">Inactivo</option>
                </select>
                </div>
            </div>
            
            <div class="grid grid-cols-2 gap-4">
                <div>
                <label class="block text-sm font-medium text-gray-300 mb-2">Área</label>
                <input
                    type="text"
                    name="department"
                    bind:value={usuarioSeleccionado.area}
                    class="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    placeholder="Ej: RRHH, IT, Casino"
                    aria-label="Área del usuario"
                />
                </div>
                
                <div>
                <label class="block text-sm font-medium text-gray-300 mb-2">Teléfono</label>
                <input
                    type="tel"
                    name="phone"
                    value={usuarioSeleccionado.telefono || ''}
                    class="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    placeholder="+56912345678"
                    aria-label="Teléfono del usuario"
                />
                </div>
            </div>
            </div>
            
            <div class="p-6 border-t border-gray-700 flex justify-end space-x-3">
            <button
                type="button"
                onclick={() => mostrarModalEditar = false}
                class="px-5 py-2.5 bg-gray-800 hover:bg-gray-700 text-white rounded-xl font-medium transition-colors"
                aria-label="Cancelar edición de usuario"
            >
                Cancelar
            </button>
            <button
                type="submit"
                disabled={isLoading}
                class="px-5 py-2.5 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white rounded-xl font-medium transition-colors flex items-center disabled:opacity-50"
                aria-label="Guardar cambios del usuario"
            >
                {#if isLoading}
                    <svg class="animate-spin h-5 w-5 mr-3 text-white" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                    </svg>
                {/if}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                Guardar Cambios
            </button>
            </div>
        </form>
      </div>
    </div>
  {/if}
  
  <!-- Modal Eliminar Usuario -->
  {#if mostrarModalEliminar && usuarioSeleccionado}
    <div class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div class="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl border border-gray-700 w-full max-w-md shadow-2xl">
        <div class="p-6 border-b border-gray-700">
          <div class="flex items-center space-x-3">
            <div class="h-12 w-12 bg-gradient-to-br from-red-600/20 to-red-700/20 rounded-xl flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </div>
            <div>
              <h2 class="text-xl font-bold text-white">Eliminar Usuario</h2>
              <p class="text-gray-400 text-sm mt-1">Esta acción no se puede deshacer</p>
            </div>
          </div>
        </div>
        
        <div class="p-6">
          <p class="text-gray-300 mb-4">
            ¿Está seguro que desea desactivar al usuario <span class="font-bold text-white">{usuarioSeleccionado.nombre}</span>?
          </p>
          <div class="bg-gray-800/50 rounded-xl p-4 mb-4">
            <p class="text-sm text-gray-400 mb-1">Rol: <span class="text-white">{usuarioSeleccionado.rol}</span></p>
            <p class="text-sm text-gray-400 mb-1">Email: <span class="text-white">{usuarioSeleccionado.email}</span></p>
            <p class="text-sm text-gray-400">Último acceso: <span class="text-white">{usuarioSeleccionado.ultimoAcceso}</span></p>
          </div>
        </div>
        
        <div class="p-6 border-t border-gray-700 flex justify-end space-x-3">
          <button
            type="button"
            onclick={() => mostrarModalEliminar = false}
            class="px-5 py-2.5 bg-gray-800 hover:bg-gray-700 text-white rounded-xl font-medium transition-colors"
            aria-label="Cancelar desactivación de usuario"
          >
            Cancelar
          </button>
          <form 
            method="POST" 
            action="?/deactivateUser" 
            use:enhance={() => {
                isLoading = true;
                return async ({ result, update }) => {
                    await update();
                    isLoading = false;
                    if (result.type === 'success') {
                        mostrarModalEliminar = false;
                    }
                };
            }}
          >
            <input type="hidden" name="id" value={usuarioSeleccionado.id} />
            <button
                type="submit"
                disabled={isLoading}
                class="px-5 py-2.5 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white rounded-xl font-medium transition-colors flex items-center disabled:opacity-50"
                aria-label="Confirmar desactivación de usuario"
            >
                {#if isLoading}
                    <svg class="animate-spin h-5 w-5 mr-3 text-white" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                    </svg>
                {/if}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Desactivar Usuario
            </button>
          </form>
        </div>
      </div>
    </div>
  {/if}
  
  <style>
    /* Estilos para scrollbar personalizada */
    .overflow-x-auto::-webkit-scrollbar {
      height: 6px;
    }
    
    .overflow-x-auto::-webkit-scrollbar-track {
      background: rgba(255, 255, 255, 0.05);
      border-radius: 3px;
    }
    
    .overflow-x-auto::-webkit-scrollbar-thumb {
      background: rgba(239, 68, 68, 0.3);
      border-radius: 3px;
    }
    
    .overflow-x-auto::-webkit-scrollbar-thumb:hover {
      background: rgba(239, 68, 68, 0.5);
    }
    
    /* Animación para modales */
    .backdrop-blur-sm {
      animation: fadeIn 0.2s ease-out;
    }
    
    @keyframes fadeIn {
      from {
        opacity: 0;
      }
      to {
        opacity: 1;
      }
    }
  </style>