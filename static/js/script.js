 document.getElementById('register-form').addEventListener('submit', async function (e) {
    e.preventDefault(); // Prevent page reload

    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    const response = await fetch('http://127.0.0.1:5000/api/register/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ name, email, password })
    });

    const result = await response.json();
    if (response.ok) {
      alert('User registered successfully!');
      console.log(result);
    } else {
      alert('Error: ' + (result.message || 'Something went wrong.'));
    }
  });




