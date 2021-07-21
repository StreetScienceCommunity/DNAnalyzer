document.addEventListener('DOMContentLoaded', () => {
  const $navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0);

  if ($navbarBurgers.length > 0) {
    $navbarBurgers.forEach(($el) => {
      $el.addEventListener('click', () => {
        const target = $el.dataset.target;
        const $target = document.getElementById(target);

        $el.classList.toggle('is-active');
        $target.classList.toggle('is-active');
      });
    });
  }
});

(function (window, document) {
  function onDocumentReady(fn) {
      if (document.attachEvent ? document.readyState === "complete" : document.readyState !== "loading") {
          fn();
      } else {
          document.addEventListener('DOMContentLoaded', fn);
      }
  }

  onDocumentReady(function () {
      // If you pass `?without-details` to an URL, it will automatically open
      // the `<details>` blocks (i.e. the Q&A sections most of the time).
      if (window.location.search.match(/\?without-details/gi)) {
          // Loop over all the `<blockquote>` tags and hide them.
          var blockquote = document.querySelectorAll('.details');
          Array.prototype.forEach.call(blockquote, function (blockquote) {
              blockquote.innerHTML = '';
              blockquote.style.display = 'none';
          });
      }
  });

})(window, document);