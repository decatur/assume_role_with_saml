document.body.style.backgroundColor = '#BBBBBB';

const form = document.getElementById('saml_form');
const payLoad = {
    SAMLResponse: form['SAMLResponse'].value
};

const input_signin_button = document.getElementById("input_signin_button");

const b = document.createElement('button');
b.type = 'button';
b.className = "css3button";
b.textContent = 'Assume Role';
input_signin_button.appendChild(b);
const status = document.createElement('pre');
status.style.fontSize = 'medium';
status.style.whiteSpace = 'break-spaces';
input_signin_button.parentElement.appendChild(status);

b.onclick = () => {
  payLoad.roleARN = form['roleIndex'].value;
  if (!payLoad.roleARN) {
    status.textContent = "⚠ Please select a role!";
    return
  }
  const url = 'http://localhost:9123/saml';
    fetch(url, {
        method: 'POST',
        headers: {
            // Do not send 'Content-Type': 'application/json', otherwise we will trigger stupid CORS preflight.
        },
        body: JSON.stringify(payLoad)
    })
        .then(response => {
          if (response.ok) {
            return response.json();
          } else {
            return response.json();
          }
        })
        .then(data => {
            if (data.error) {
                status.textContent = `⚠ ${url}: ${data.error}`;
            } else {
                status.textContent = `${url}: ${JSON.stringify(data)}`;
            }
        })
        .catch(e => {
          status.textContent = `⚠ ${url}: ${e}`;
          if (e.name === 'TypeError') {
              status.textContent += '; Did you start the assume role server?';
          }
        });
};