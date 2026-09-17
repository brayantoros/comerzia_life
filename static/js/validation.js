// Validación para login y register con mensajes inline
function showFieldError(input, message){
  let err = input.parentElement.querySelector('.field-error');
  if(!err){
    err = document.createElement('div');
    err.className = 'field-error';
    input.parentElement.appendChild(err);
  }
  err.textContent = message;
  err.style.display = 'block';
}

function clearFieldError(input){
  const err = input.parentElement.querySelector('.field-error');
  if(err) err.style.display = 'none';
}

document.addEventListener('DOMContentLoaded', function(){
  // Formularios de autenticación
  const loginForm = document.getElementById('loginForm');
  if(loginForm){
    loginForm.addEventListener('submit', function(e){
      const user = document.getElementById('username');
      const pass = document.getElementById('password');
      let ok = true;
      clearFieldError(user); clearFieldError(pass);
      if(!user.value.trim()){ showFieldError(user, 'El usuario es obligatorio'); ok = false; }
      if(!pass.value){ showFieldError(pass, 'La contraseña es obligatoria'); ok = false; }
      if(!ok) e.preventDefault();
    });
  }

  const registerForm = document.getElementById('registerForm');
  if(registerForm){
    registerForm.addEventListener('submit', function(e){
      const user = document.getElementById('username');
      const pass = document.getElementById('password');
      let ok = true;
      clearFieldError(user); clearFieldError(pass);
      if(!user.value.trim()){ showFieldError(user, 'El usuario es obligatorio'); ok = false; }
      if(!pass.value){ showFieldError(pass, 'La contraseña es obligatoria'); ok = false; }
      if(pass.value && pass.value.length < 6){ showFieldError(pass, 'Mínimo 6 caracteres'); ok = false; }
      if(!ok) e.preventDefault();
    });
  }
});
