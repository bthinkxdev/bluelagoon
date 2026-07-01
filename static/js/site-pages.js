(function () {
  /* Scroll reveal */
  var revealEls = document.querySelectorAll('.wl-reveal');
  if (revealEls.length && 'IntersectionObserver' in window) {
    var revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

    revealEls.forEach(function (el) {
      if (!el.classList.contains('is-visible')) {
        revealObserver.observe(el);
      }
    });
  } else {
    revealEls.forEach(function (el) {
      el.classList.add('is-visible');
    });
  }

  /* Back to top */
  var toTop = document.getElementById('wl-to-top');
  if (toTop) {
    function toggleToTop() {
      if (window.scrollY > 400) {
        toTop.hidden = false;
      } else {
        toTop.hidden = true;
      }
    }
    window.addEventListener('scroll', toggleToTop, { passive: true });
    toggleToTop();
    toTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* Inner pages: header always solid */
  if (document.body.classList.contains('wl-inner-page')) {
    document.body.classList.add('wl-header-solid');
  }

  /* Package detail section subnav */
  var subnavLinks = document.querySelectorAll('.wl-detail-subnav__link');
  if (subnavLinks.length) {
    var sectionIds = [];
    subnavLinks.forEach(function (link) {
      var href = link.getAttribute('href');
      if (href && href.charAt(0) === '#') {
        sectionIds.push(href.slice(1));
      }
      link.addEventListener('click', function () {
        subnavLinks.forEach(function (l) { l.classList.remove('is-active'); });
        link.classList.add('is-active');
      });
    });

    if ('IntersectionObserver' in window) {
      var sections = sectionIds.map(function (id) { return document.getElementById(id); }).filter(Boolean);
      var sectionObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var id = entry.target.id;
          subnavLinks.forEach(function (link) {
            link.classList.toggle('is-active', link.getAttribute('href') === '#' + id);
          });
        });
      }, { rootMargin: '-40% 0px -50% 0px', threshold: 0 });

      sections.forEach(function (section) {
        sectionObserver.observe(section);
      });
    }
  }

  /* Package detail gallery */
  document.querySelectorAll('[data-gallery]').forEach(function (gallery) {
    var main = gallery.querySelector('[data-gallery-main]');
    var thumbs = Array.prototype.slice.call(gallery.querySelectorAll('[data-gallery-thumb]'));
    var prevBtn = gallery.querySelector('[data-gallery-prev]');
    var nextBtn = gallery.querySelector('[data-gallery-next]');
    var zoomBtn = gallery.querySelector('[data-gallery-zoom]');
    var counter = gallery.querySelector('[data-gallery-counter]');
    var lightbox = document.getElementById('wl-gallery-lightbox');
    var lightboxImg = lightbox ? lightbox.querySelector('[data-lightbox-img]') : null;
    var lightboxClose = lightbox ? lightbox.querySelector('[data-lightbox-close]') : null;
    var lightboxPrev = lightbox ? lightbox.querySelector('[data-lightbox-prev]') : null;
    var lightboxNext = lightbox ? lightbox.querySelector('[data-lightbox-next]') : null;
    if (!main) return;

    var currentIndex = 0;
    var touchStartX = 0;
    var autoplayMs = parseInt(gallery.getAttribute('data-gallery-autoplay') || '0', 10);
    var autoplayTimer = null;
    var autoplayHoverPaused = false;
    var autoplayVisible = true;
    var prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function clearAutoplay() {
      if (autoplayTimer) {
        clearInterval(autoplayTimer);
        autoplayTimer = null;
      }
    }

    function canAutoplay() {
      return autoplayMs > 0
        && thumbs.length > 1
        && !prefersReducedMotion
        && autoplayVisible
        && !autoplayHoverPaused
        && (!lightbox || lightbox.hidden)
        && document.visibilityState !== 'hidden';
    }

    function startAutoplay() {
      clearAutoplay();
      if (!canAutoplay()) return;
      autoplayTimer = setInterval(function () {
        if (!canAutoplay()) return;
        showSlide(currentIndex + 1);
      }, autoplayMs);
    }

    function restartAutoplay() {
      clearAutoplay();
      startAutoplay();
    }

    function slideSources() {
      return thumbs.map(function (thumb) {
        return {
          src: thumb.getAttribute('data-src') || '',
          alt: thumb.getAttribute('data-alt') || main.alt || ''
        };
      });
    }

    function showSlide(index) {
      var sources = slideSources();
      if (!sources.length) return;
      currentIndex = (index + sources.length) % sources.length;
      var slide = sources[currentIndex];
      if (!slide.src) return;

      main.src = slide.src;
      main.alt = slide.alt;
      if (lightboxImg && lightbox && !lightbox.hidden) {
        lightboxImg.src = slide.src;
        lightboxImg.alt = slide.alt;
      }

      thumbs.forEach(function (t, i) {
        var active = i === currentIndex;
        t.classList.toggle('is-active', active);
        t.setAttribute('aria-selected', active ? 'true' : 'false');
      });

      var activeThumb = thumbs[currentIndex];
      if (activeThumb) {
        activeThumb.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
      }

      if (counter) {
        counter.textContent = (currentIndex + 1) + ' / ' + sources.length;
      }

      restartAutoplay();
    }

    thumbs.forEach(function (thumb, index) {
      thumb.addEventListener('click', function () {
        showSlide(index);
      });
    });

    if (prevBtn) {
      prevBtn.addEventListener('click', function () {
        showSlide(currentIndex - 1);
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener('click', function () {
        showSlide(currentIndex + 1);
      });
    }

    if (thumbs.length > 1) {
      gallery.addEventListener('keydown', function (event) {
        if (event.key === 'ArrowLeft') showSlide(currentIndex - 1);
        if (event.key === 'ArrowRight') showSlide(currentIndex + 1);
      });

      gallery.addEventListener('touchstart', function (event) {
        touchStartX = event.changedTouches[0].screenX;
      }, { passive: true });

      gallery.addEventListener('touchend', function (event) {
        var delta = event.changedTouches[0].screenX - touchStartX;
        if (Math.abs(delta) < 40) return;
        if (delta > 0) showSlide(currentIndex - 1);
        else showSlide(currentIndex + 1);
      }, { passive: true });

      gallery.addEventListener('mouseenter', function () {
        autoplayHoverPaused = true;
        clearAutoplay();
      });

      gallery.addEventListener('mouseleave', function () {
        autoplayHoverPaused = false;
        startAutoplay();
      });

      gallery.addEventListener('focusin', function () {
        autoplayHoverPaused = true;
        clearAutoplay();
      });

      gallery.addEventListener('focusout', function () {
        autoplayHoverPaused = false;
        startAutoplay();
      });

      if ('IntersectionObserver' in window) {
        var galleryObserver = new IntersectionObserver(function (entries) {
          entries.forEach(function (entry) {
            autoplayVisible = entry.isIntersecting;
            if (autoplayVisible) startAutoplay();
            else clearAutoplay();
          });
        }, { threshold: 0.35 });
        galleryObserver.observe(gallery);
      }

      document.addEventListener('visibilitychange', function () {
        if (document.visibilityState === 'hidden') clearAutoplay();
        else startAutoplay();
      });

      startAutoplay();
    } else {
      if (prevBtn) prevBtn.hidden = true;
      if (nextBtn) nextBtn.hidden = true;
    }

    main.addEventListener('error', function () {
      var fallback = main.getAttribute('data-fallback');
      if (fallback && main.src.indexOf(fallback) === -1) {
        main.src = fallback;
      }
    });

    function openLightbox() {
      if (!lightbox || !lightboxImg) return;
      clearAutoplay();
      lightboxImg.src = main.src;
      lightboxImg.alt = main.alt;
      lightbox.hidden = false;
      lightbox.setAttribute('aria-hidden', 'false');
      document.body.classList.add('wl-lightbox-open');
    }

    function closeLightbox() {
      if (!lightbox) return;
      lightbox.hidden = true;
      lightbox.setAttribute('aria-hidden', 'true');
      document.body.classList.remove('wl-lightbox-open');
      startAutoplay();
    }

    if (zoomBtn) {
      zoomBtn.addEventListener('click', openLightbox);
    }

    if (lightboxClose) {
      lightboxClose.addEventListener('click', closeLightbox);
    }

    if (lightbox) {
      lightbox.addEventListener('click', function (event) {
        if (event.target === lightbox) closeLightbox();
      });
    }

    if (lightboxPrev) {
      lightboxPrev.addEventListener('click', function () {
        showSlide(currentIndex - 1);
      });
    }

    if (lightboxNext) {
      lightboxNext.addEventListener('click', function () {
        showSlide(currentIndex + 1);
      });
    }

    document.addEventListener('keydown', function (event) {
      if (!lightbox || lightbox.hidden) return;
      if (event.key === 'Escape') closeLightbox();
      if (event.key === 'ArrowLeft') showSlide(currentIndex - 1);
      if (event.key === 'ArrowRight') showSlide(currentIndex + 1);
    });
  });

  /* Package list — AJAX category filter + sort/duration */
  var packagePanel = document.getElementById('wl-package-list-panel');
  if (packagePanel) {
    var partialUrl = packagePanel.getAttribute('data-partial-url');
    var resultsRoot = document.getElementById('wl-package-results');
    var resultsMain = document.getElementById('wl-package-results-main');
    var filterTabs = packagePanel.querySelectorAll('[data-package-filter]');
    var listControls = packagePanel.querySelectorAll('[data-package-list-control]');
    var durationChips = packagePanel.querySelectorAll('[data-package-duration-chip]');
    var clearFiltersBtn = packagePanel.querySelector('[data-package-clear-filters]');
    var filterAbort = null;

    function hasActiveListFilters() {
      var params = new URL(window.location.href).searchParams;
      var sort = params.get('sort') || 'default';
      var duration = params.get('duration') || '';
      return (sort && sort !== 'default') || Boolean(duration);
    }

    function updateClearFiltersVisibility() {
      if (!clearFiltersBtn) return;
      clearFiltersBtn.hidden = !hasActiveListFilters();
    }

    function getCurrentCategory() {
      var activeTab = packagePanel.querySelector('[data-package-filter].is-active[data-category]');
      if (activeTab) {
        return activeTab.getAttribute('data-category') || '';
      }
      return new URL(window.location.href).searchParams.get('category') || '';
    }

    function buildListQuery(overrides) {
      var url = new URL(window.location.href);
      if (overrides) {
        Object.keys(overrides).forEach(function (key) {
          var value = overrides[key];
          if (value === null || value === undefined || value === '') {
            url.searchParams.delete(key);
          } else {
            url.searchParams.set(key, value);
          }
        });
        if (Object.prototype.hasOwnProperty.call(overrides, 'category') && !overrides.category) {
          url.searchParams.delete('tab');
        }
      }
      return url.searchParams.toString();
    }

    function syncListControlsFromUrl() {
      var params = new URL(window.location.href).searchParams;
      listControls.forEach(function (control) {
        var name = control.getAttribute('data-package-list-control');
        if (!name) return;
        var value = params.get(name);
        if (name === 'sort' && !value) {
          value = 'default';
        }
        if (name === 'duration' && !value) {
          value = '';
        }
        if (control.value !== value) {
          control.value = value;
        }
      });

      durationChips.forEach(function (chip) {
        var chipValue = chip.getAttribute('data-value') || '';
        var active = (params.get('duration') || '') === chipValue;
        chip.classList.toggle('is-active', active);
        chip.setAttribute('aria-pressed', active ? 'true' : 'false');
      });

      updateClearFiltersVisibility();
    }

    function setActiveFilterTab(category) {
      filterTabs.forEach(function (tab) {
        var tabCategory = tab.getAttribute('data-category') || '';
        var active = tabCategory === (category || '');
        tab.classList.toggle('is-active', active);
        tab.classList.toggle('is-loading', false);
        tab.setAttribute('aria-selected', active ? 'true' : 'false');
      });

      document.querySelectorAll('.wl-search-tab').forEach(function (tab) {
        var tabCategory = tab.getAttribute('data-tab') || '';
        var active = tabCategory === (category || '');
        tab.classList.toggle('is-active', active);
        tab.setAttribute('aria-selected', active ? 'true' : 'false');
      });

      var categoryField = document.getElementById('wl-search-category');
      if (categoryField) {
        categoryField.value = category || '';
      }
    }

    function updateBrowserUrl(overrides) {
      var url = new URL(window.location.href);
      if (overrides) {
        Object.keys(overrides).forEach(function (key) {
          var value = overrides[key];
          if (value === null || value === undefined || value === '') {
            url.searchParams.delete(key);
          } else {
            url.searchParams.set(key, value);
          }
        });
        if (Object.prototype.hasOwnProperty.call(overrides, 'category') && !overrides.category) {
          url.searchParams.delete('tab');
        }
      }
      var category = url.searchParams.get('category') || '';
      window.history.pushState({ packageCategory: category }, '', url);
    }

    function revealNewResults() {
      if (!resultsMain) return;
      resultsMain.querySelectorAll('.wl-reveal').forEach(function (el) {
        el.classList.add('is-visible');
      });
    }

    function loadPackages(overrides, options) {
      options = options || {};
      if (!partialUrl || !resultsMain) return;

      if (filterAbort) {
        filterAbort.abort();
      }
      filterAbort = new AbortController();

      var category = overrides && Object.prototype.hasOwnProperty.call(overrides, 'category')
        ? overrides.category
        : getCurrentCategory();

      if (resultsRoot) {
        resultsRoot.classList.add('wl-package-results--loading');
        resultsRoot.setAttribute('aria-busy', 'true');
      }
      resultsMain.classList.add('is-swapping');

      filterTabs.forEach(function (tab) {
        var tabCategory = tab.getAttribute('data-category') || '';
        tab.classList.toggle('is-loading', tabCategory === (category || ''));
      });

      var query = buildListQuery(overrides);
      var fetchUrl = partialUrl + (query ? '?' + query : '');

      fetch(fetchUrl, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        signal: filterAbort.signal
      })
        .then(function (response) {
          if (!response.ok) throw new Error('Filter request failed');
          return response.text();
        })
        .then(function (html) {
          resultsMain.innerHTML = html;
          resultsMain.classList.remove('is-swapping');
          if (resultsRoot) {
            resultsRoot.classList.remove('wl-package-results--loading');
            resultsRoot.setAttribute('aria-busy', 'false');
          }
          filterTabs.forEach(function (tab) {
            tab.classList.remove('is-loading');
          });
          setActiveFilterTab(category);
          if (!options.skipUrl) {
            updateBrowserUrl(overrides);
          }
          syncListControlsFromUrl();
          revealNewResults();
          if (!options.skipScroll && resultsRoot) {
            var top = resultsRoot.getBoundingClientRect().top + window.scrollY - 88;
            window.scrollTo({ top: Math.max(top, 0), behavior: 'smooth' });
          }
        })
        .catch(function (error) {
          if (error.name === 'AbortError') return;
          resultsMain.classList.remove('is-swapping');
          if (resultsRoot) {
            resultsRoot.classList.remove('wl-package-results--loading');
            resultsRoot.setAttribute('aria-busy', 'false');
          }
          filterTabs.forEach(function (tab) {
            tab.classList.remove('is-loading');
          });
          setActiveFilterTab(category);
        });
    }

    packagePanel.addEventListener('click', function (event) {
      var trigger = event.target.closest('[data-package-filter]');
      if (!trigger || !packagePanel.contains(trigger)) return;
      event.preventDefault();

      var category = trigger.getAttribute('data-category') || '';
      if (trigger.classList.contains('is-active') && !trigger.classList.contains('wl-btn')) return;

      setActiveFilterTab(category);
      loadPackages({ category: category });
    });

    listControls.forEach(function (control) {
      control.addEventListener('change', function () {
        var name = control.getAttribute('data-package-list-control');
        if (!name) return;
        var value = control.value;
        var overrides = {};
        overrides[name] = value;
        if (name === 'sort' && value === 'default') {
          overrides.sort = '';
        }
        if (name === 'duration' && !value) {
          overrides.duration = '';
        }
        loadPackages(overrides);
      });
    });

    durationChips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        var value = chip.getAttribute('data-value') || '';
        if (chip.classList.contains('is-active')) return;
        durationChips.forEach(function (item) {
          var active = item === chip;
          item.classList.toggle('is-active', active);
          item.setAttribute('aria-pressed', active ? 'true' : 'false');
        });
        loadPackages({ duration: value });
      });
    });

    if (clearFiltersBtn) {
      clearFiltersBtn.addEventListener('click', function () {
        var sortSelect = document.getElementById('wl-package-sort');
        if (sortSelect) {
          sortSelect.value = 'default';
        }
        durationChips.forEach(function (chip, index) {
          var active = index === 0;
          chip.classList.toggle('is-active', active);
          chip.setAttribute('aria-pressed', active ? 'true' : 'false');
        });
        loadPackages({ sort: '', duration: '' });
      });
    }

    updateClearFiltersVisibility();

    window.addEventListener('popstate', function () {
      var category = new URL(window.location.href).searchParams.get('category') || '';
      setActiveFilterTab(category);
      syncListControlsFromUrl();
      loadPackages(null, { skipUrl: true, skipScroll: true });
    });

    if (!window.history.state || typeof window.history.state.packageCategory === 'undefined') {
      var initialCategory = new URL(window.location.href).searchParams.get('category') || '';
      window.history.replaceState({ packageCategory: initialCategory }, '', window.location.href);
    }
  }
})();
