const button = document.getElementById("testButton");
const result = document.getElementById("result");

button.addEventListener("click", () => {
  result.textContent =
    "JavaScript loaded successfully — WebChain deployment test passed!";
});
