function getCookie(name) {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? decodeURIComponent(match[2]) : null;
}

document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('contactForm');
  if (!form) return;

  const submitBtn = form.querySelector('button[type="submit"]');
  const originalBtnHtml = submitBtn.innerHTML;

  function setFieldError(id, msg) {
    const field = document.getElementById(id);
    field.classList.toggle('is-invalid', !!msg);
    let feedback = field.parentElement.querySelector('.invalid-feedback');
    if (!feedback) {
      feedback = document.createElement('div');
      feedback.className = 'invalid-feedback';
      field.parentElement.appendChild(feedback);
    }
    feedback.textContent = msg || '';
  }

  function showStatus(message, isError) {
    let status = form.querySelector('.form-status');
    if (!status) {
      status = document.createElement('div');
      status.className = 'form-status col-12';
      form.appendChild(status);
    }
    status.textContent = message;
    status.style.color = isError ? '#dc3545' : '#198754';
  }

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    ['cName', 'cEmail', 'cMsg'].forEach((id) => setFieldError(id, null));

    const payload = {
      name: document.getElementById('cName').value.trim(),
      email: document.getElementById('cEmail').value.trim(),
      message: document.getElementById('cMsg').value.trim(),
    };

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Sending…';

    try {
      const res = await fetch('/contact/submit/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify(payload),
      });
      const data = await res.json();

      if (data.ok) {
        showStatus(data.message, false);
        form.reset();
      } else {
        const fieldMap = { name: 'cName', email: 'cEmail', message: 'cMsg' };
        Object.entries(data.errors || {}).forEach(([key, msg]) => {
          if (fieldMap[key]) setFieldError(fieldMap[key], msg);
        });
        showStatus('Please fix the highlighted fields.', true);
      }
    } catch (err) {
      showStatus('Something went wrong — please try again.', true);
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalBtnHtml;
    }
  });
});