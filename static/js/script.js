window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

function deleteVenue(id){
  fetch(`/venues/${id}`,{
    method: 'DELETE',
    redirect: 'follow'
  }).then(response => {
    // HTTP 301 response
    if (response.redirected) {
      window.location.href = response.url;
    }
  }).catch((error) => {
    console.error('Error:', error);
  });
}