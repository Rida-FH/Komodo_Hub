document.getElementById('forum').addEventListener('submit', function (event) {
event.preventDefault(); // Prevent the form from submitting and reloading the page
console.log('Form submission prevented');

// Get the text and image from the form
const postText = document.getElementById('postInput').value;
const fileInput = document.getElementById('fileInput');
const file = fileInput.files[0];

console.log('Post Text:', postText); // Check if the text is being captured
console.log('File:', file); // Check if the file is being captured

// Create a new post element
const postElement = document.createElement('div');
postElement.classList.add('post');

// Add text to the post
if (postText) {
    const textElement = document.createElement('p');
    textElement.textContent = postText;
    postElement.appendChild(textElement);
}

// Add image to the post (if uploaded)
if (file) {
    const reader = new FileReader();
    reader.onload = function (e) {
        console.log('Image loaded:', e.target.result); // Check if the image is being read
        const imgElement = document.createElement('img');
        imgElement.src = e.target.result;
        imgElement.classList.add('postImage');
        postElement.appendChild(imgElement);
    };
    reader.readAsDataURL(file); // Read the image file as a data URL
}

// Append the post to the posts container
document.getElementById('postsContainer').appendChild(postElement);
console.log('Post added to container'); // Check if the post is being appended

// Clear the form
document.getElementById('postInput').value = ''; // Clear the text area
fileInput.value = ''; // Clear the file input
}); 
