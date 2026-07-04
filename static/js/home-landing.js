(function () {
  var navToggle = document.querySelector('.wl-nav-toggle');
  var nav = document.getElementById('wl-nav');
  var tabs = document.querySelectorAll('.wl-search-tab');
  var modal = document.getElementById('wl-dest-modal');
  var modalImage = document.getElementById('wl-modal-image');
  var modalTitle = document.getElementById('wl-modal-title');
  var modalBody = document.getElementById('wl-modal-body');
  var modalLink = document.getElementById('wl-modal-link');
  var loveModal = document.getElementById('wl-love-modal');
  var loveModalImage = document.getElementById('wl-love-modal-image');
  var loveModalTitle = document.getElementById('wl-love-modal-title');
  var loveModalBody = document.getElementById('wl-love-modal-body');
  var loveModalLink = document.getElementById('wl-love-modal-link');
  var partnerModal = document.getElementById('wl-partner-modal');
  var partnerModalImage = document.getElementById('wl-partner-modal-image');
  var partnerModalLabel = document.getElementById('wl-partner-modal-label');
  var partnerModalTitle = document.getElementById('wl-partner-modal-title');
  var partnerModalBody = document.getElementById('wl-partner-modal-body');
  var partnerModalLink = document.getElementById('wl-partner-modal-link');
  var modalLastFocus = null;

  function closeWlModal(modalEl) {
    if (!modalEl || modalEl.hidden) return;
    modalEl.hidden = true;
    modalEl.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('wl-modal-open');
    if (modalLastFocus && modalLastFocus.focus) modalLastFocus.focus();
    modalLastFocus = null;
  }

  function openWlModal(modalEl, config) {
    if (!modalEl) return;

    if (config.imageEl) {
      config.imageEl.src = config.image || '';
      config.imageEl.alt = config.title || '';
    }
    if (config.labelEl) config.labelEl.textContent = config.label || 'Partner details';
    if (config.titleEl) config.titleEl.textContent = config.title || '';
    if (config.bodyEl) {
      if (config.bodyHtml) {
        config.bodyEl.innerHTML = config.bodyHtml;
      } else {
        config.bodyEl.textContent = config.body || '';
      }
    }
    if (config.linkEl) {
      config.linkEl.href = config.link || '#';
      config.linkEl.textContent = config.linkLabel || 'Learn more';
      if (config.external) {
        config.linkEl.setAttribute('target', '_blank');
        config.linkEl.setAttribute('rel', 'noopener noreferrer');
      } else {
        config.linkEl.removeAttribute('target');
        config.linkEl.removeAttribute('rel');
      }
    }

    modalLastFocus = document.activeElement;
    modalEl.hidden = false;
    modalEl.setAttribute('aria-hidden', 'false');
    document.body.classList.add('wl-modal-open');

    var closeBtn = modalEl.querySelector('.wl-modal__close');
    if (closeBtn) closeBtn.focus();
  }

  function partnerBodyHtml(text) {
    return (text || '')
      .split(/\n\s*\n/)
      .map(function (part) { return part.trim(); })
      .filter(Boolean)
      .map(function (part) {
        return '<p>' + part.replace(/</g, '&lt;').replace(/>/g, '&gt;') + '</p>';
      })
      .join('');
  }

  document.querySelectorAll('[data-partner-open]').forEach(function (button) {
    button.addEventListener('click', function () {
      openWlModal(partnerModal, {
        imageEl: partnerModalImage,
        labelEl: partnerModalLabel,
        titleEl: partnerModalTitle,
        bodyEl: partnerModalBody,
        linkEl: partnerModalLink,
        image: button.getAttribute('data-partner-image') || '',
        label: button.getAttribute('data-partner-label') || 'Partner details',
        title: button.getAttribute('data-partner-title') || '',
        bodyHtml: partnerBodyHtml(button.getAttribute('data-partner-body') || ''),
        link: button.getAttribute('data-partner-link') || '#',
        linkLabel: button.getAttribute('data-partner-link-label') || 'Learn more',
        external: button.getAttribute('data-partner-external') === 'true'
      });
    });
  });

  [modal, loveModal, partnerModal].forEach(function (modalEl) {
    if (!modalEl) return;
    modalEl.querySelectorAll('[data-wl-modal-close]').forEach(function (el) {
      el.addEventListener('click', function () {
        closeWlModal(modalEl);
      });
    });
  });

  /* Solid header after scrolling past hero */
  function updateHeaderSolid() {
    if (!document.body.classList.contains('home-wanderly')) return;
    if (document.body.classList.contains('wl-nav-open')) {
      document.body.classList.add('wl-header-solid');
      return;
    }
    var hero = document.querySelector('.wl-hero-carousel, .wl-main > .wl-hero');
    var headerHeight = window.matchMedia('(max-width: 767px)').matches ? 64 : 72;
    var solid = false;
    if (hero) {
      solid = hero.getBoundingClientRect().bottom < headerHeight + 8;
    } else {
      solid = window.scrollY > headerHeight;
    }
    document.body.classList.toggle('wl-header-solid', solid);
  }

  if (document.body.classList.contains('home-wanderly')) {
    window.addEventListener('scroll', updateHeaderSolid, { passive: true });
    window.addEventListener('resize', updateHeaderSolid);
    updateHeaderSolid();
  }

  if (navToggle && nav) {
    var packagesAutoTimer = null;
    var navCloseTimer = null;

    function setDropdownExpanded(dropdown, expanded) {
      if (!dropdown) return;
      dropdown.classList.toggle('is-expanded', expanded);
      var toggle = dropdown.querySelector('.wl-nav__submenu-toggle');
      if (toggle) {
        toggle.setAttribute('aria-expanded', expanded ? 'true' : 'false');
      }
    }

    function collapseOtherDropdowns(activeDropdown) {
      nav.querySelectorAll('.wl-nav__dropdown.is-expanded').forEach(function (item) {
        if (item !== activeDropdown) {
          setDropdownExpanded(item, false);
        }
      });
    }

    function schedulePackagesAutoExpand() {
      clearTimeout(packagesAutoTimer);
      if (window.innerWidth > 991) return;
      packagesAutoTimer = setTimeout(function () {
        if (!nav.classList.contains('is-open')) return;
        var packagesDropdown = nav.querySelector('.wl-nav__dropdown');
        if (!packagesDropdown) return;
        collapseOtherDropdowns(packagesDropdown);
        setDropdownExpanded(packagesDropdown, true);
      }, 1000);
    }

    function setNavOpen(open) {
      clearTimeout(navCloseTimer);
      clearTimeout(packagesAutoTimer);

      if (open) {
        document.body.classList.remove('wl-nav-closing');
        nav.classList.remove('is-closing');
        nav.classList.add('is-open');
        navToggle.setAttribute('aria-expanded', 'true');
        navToggle.setAttribute('aria-label', 'Close menu');
        document.body.classList.add('wl-nav-open');
        schedulePackagesAutoExpand();
      } else if (nav.classList.contains('is-open')) {
        nav.classList.add('is-closing');
        nav.classList.remove('is-open');
        document.body.classList.add('wl-nav-closing');
        document.body.classList.remove('wl-nav-open');
        navToggle.setAttribute('aria-expanded', 'false');
        navToggle.setAttribute('aria-label', 'Open menu');

        nav.querySelectorAll('.wl-nav__dropdown').forEach(function (dropdown) {
          if (!dropdown.querySelector('.wl-nav__dropdown-row > a.is-active')) {
            setDropdownExpanded(dropdown, false);
          }
        });

        navCloseTimer = setTimeout(function () {
          nav.classList.remove('is-closing');
          document.body.classList.remove('wl-nav-closing');
        }, 360);
      } else {
        navToggle.setAttribute('aria-expanded', 'false');
        navToggle.setAttribute('aria-label', 'Open menu');
        document.body.classList.remove('wl-nav-open', 'wl-nav-closing');
      }

      updateHeaderSolid();

      if (open) {
        var travellersPicker = document.getElementById('wl-travellers-picker');
        if (travellersPicker && travellersPicker.classList.contains('is-open')) {
          travellersPicker.classList.remove('is-open');
          var panel = document.getElementById('wl-travellers-panel');
          var trigger = travellersPicker.querySelector('.wl-travellers__trigger');
          if (panel) panel.hidden = true;
          if (trigger) trigger.setAttribute('aria-expanded', 'false');
          var searchWrap = travellersPicker.closest('.wl-search-wrap');
          if (searchWrap) searchWrap.classList.remove('wl-search-travellers-open');
        }
      }
    }

    navToggle.addEventListener('click', function () {
      setNavOpen(!nav.classList.contains('is-open'));
    });

    var navClose = nav.querySelector('.wl-nav__close');
    if (navClose) {
      navClose.addEventListener('click', function () {
        setNavOpen(false);
      });
    }

    nav.querySelectorAll('.wl-nav__submenu-toggle').forEach(function (toggle) {
      toggle.addEventListener('click', function (event) {
        if (window.innerWidth > 991) return;
        event.preventDefault();
        event.stopPropagation();
        var dropdown = toggle.closest('.wl-nav__dropdown');
        if (!dropdown) return;
        var expanded = !dropdown.classList.contains('is-expanded');
        collapseOtherDropdowns(expanded ? dropdown : null);
        setDropdownExpanded(dropdown, expanded);
      });
    });

    nav.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        setNavOpen(false);
      });
    });

    document.addEventListener('click', function (e) {
      if (!nav.classList.contains('is-open')) return;
      if (nav.contains(e.target) || navToggle.contains(e.target)) return;
      setNavOpen(false);
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('is-open')) {
        setNavOpen(false);
      }
    });

    window.addEventListener('resize', function () {
      if (window.innerWidth > 991 && nav.classList.contains('is-open')) {
        setNavOpen(false);
      }
    });
  }

  var searchForm = document.getElementById('wl-search-form');

  tabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      tabs.forEach(function (t) {
        t.classList.remove('is-active');
        t.setAttribute('aria-selected', 'false');
      });
      tab.classList.add('is-active');
      tab.setAttribute('aria-selected', 'true');
      var categoryField = document.getElementById('wl-search-category');
      if (categoryField) {
        categoryField.value = tab.dataset.tab || '';
      }
      if (window.wlHideDestinationSuggestions) {
        window.wlHideDestinationSuggestions();
      }
    });
  });

  var activeTab = document.querySelector('.wl-search-tab.is-active');
  var categoryField = document.getElementById('wl-search-category');
  if (activeTab && categoryField) {
    categoryField.value = activeTab.dataset.tab || '';
  }

  /* Travel date picker */
  function initSearchDatePickers() {
    if (typeof flatpickr === 'undefined') return;

    var departInput = document.getElementById('wl-depart');
    if (!departInput) return;

    var departDefault = departInput.value ? departInput.value : null;
    if (!departDefault) {
      departDefault = new Date();
      departDefault.setDate(departDefault.getDate() + 7);
    }

    function syncCalendarWidth(instance) {
      var field = instance.element.closest('.wl-search-field');
      if (!field || !instance.calendarContainer) return;
      var width = Math.max(field.offsetWidth, 260);
      instance.calendarContainer.style.width = width + 'px';
      instance.calendarContainer.style.minWidth = width + 'px';
    }

    flatpickr(departInput, {
      altInput: true,
      altFormat: 'j M, Y',
      altInputClass: 'wl-date-alt',
      dateFormat: 'Y-m-d',
      defaultDate: departDefault,
      minDate: 'today',
      disableMobile: true,
      allowInput: false,
      clickOpens: true,
      onReady: function (_dates, _str, instance) {
        instance.calendarContainer.classList.add('wl-flatpickr');
      },
      onOpen: function (_dates, _str, instance) {
        syncCalendarWidth(instance);
      }
    });

    document.querySelectorAll('.wl-search-field--date').forEach(function (field) {
      field.addEventListener('click', function (e) {
        if (e.target.closest('.flatpickr-calendar')) return;
        var input = field.querySelector('#wl-depart');
        if (input && input._flatpickr) {
          input._flatpickr.open();
        }
      });
    });
  }

  initSearchDatePickers();

  /* Destination autocomplete */
  (function initDestinationAutocomplete() {
    var form = document.getElementById('wl-search-form');
    var input = document.getElementById('wl-destination');
    var list = document.getElementById('wl-destination-suggestions');
    if (!form || !input || !list) return;

    var apiUrl = form.getAttribute('data-destinations-url') || '/api/destinations/';
    var debounceTimer = null;
    var activeIndex = -1;
    var items = [];
    var abortController = null;

    function hideSuggestions() {
      list.hidden = true;
      list.innerHTML = '';
      items = [];
      activeIndex = -1;
      input.setAttribute('aria-expanded', 'false');
    }

    window.wlHideDestinationSuggestions = hideSuggestions;

    function renderSuggestions(results) {
      items = results || [];
      activeIndex = -1;
      list.innerHTML = '';

      if (!items.length) {
        hideSuggestions();
        return;
      }

      items.forEach(function (item, index) {
        var li = document.createElement('li');
        li.className = 'wl-destination-suggestions__item';
        li.setAttribute('role', 'option');
        li.setAttribute('id', 'wl-destination-option-' + index);
        li.textContent = item.name;
        li.addEventListener('mousedown', function (event) {
          event.preventDefault();
          input.value = item.name;
          hideSuggestions();
          input.focus();
        });
        list.appendChild(li);
      });

      list.hidden = false;
      input.setAttribute('aria-expanded', 'true');
    }

    function setActive(index) {
      var options = list.querySelectorAll('.wl-destination-suggestions__item');
      options.forEach(function (option, i) {
        option.classList.toggle('is-active', i === index);
      });
      activeIndex = index;
      if (index >= 0 && options[index]) {
        input.setAttribute('aria-activedescendant', options[index].id);
      } else {
        input.removeAttribute('aria-activedescendant');
      }
    }

    function fetchSuggestions(query) {
      if (abortController) abortController.abort();
      abortController = typeof AbortController !== 'undefined' ? new AbortController() : null;

      var categoryField = document.getElementById('wl-search-category');
      var travelType = categoryField ? categoryField.value : '';
      var url = apiUrl + '?search=' + encodeURIComponent(query);
      if (travelType) {
        url += '&travel_type=' + encodeURIComponent(travelType);
      }

      fetch(url, {
        headers: { Accept: 'application/json' },
        signal: abortController ? abortController.signal : undefined
      })
        .then(function (response) {
          if (!response.ok) throw new Error('Destination lookup failed');
          return response.json();
        })
        .then(renderSuggestions)
        .catch(function (error) {
          if (error && error.name === 'AbortError') return;
          hideSuggestions();
        });
    }

    input.addEventListener('input', function () {
      var query = input.value.trim();
      clearTimeout(debounceTimer);
      if (query.length < 1) {
        hideSuggestions();
        return;
      }
      debounceTimer = setTimeout(function () {
        fetchSuggestions(query);
      }, 300);
    });

    input.addEventListener('keydown', function (event) {
      if (list.hidden || !items.length) return;
      if (event.key === 'ArrowDown') {
        event.preventDefault();
        setActive(activeIndex < items.length - 1 ? activeIndex + 1 : 0);
      } else if (event.key === 'ArrowUp') {
        event.preventDefault();
        setActive(activeIndex > 0 ? activeIndex - 1 : items.length - 1);
      } else if (event.key === 'Enter' && activeIndex >= 0) {
        event.preventDefault();
        input.value = items[activeIndex].name;
        hideSuggestions();
      } else if (event.key === 'Escape') {
        hideSuggestions();
      }
    });

    input.addEventListener('blur', function () {
      setTimeout(hideSuggestions, 120);
    });

    document.addEventListener('click', function (event) {
      if (!event.target.closest('.wl-destination-autocomplete')) {
        hideSuggestions();
      }
    });
  })();

  /* Travellers picker */
  var travellersPicker = document.getElementById('wl-travellers-picker');
  if (travellersPicker) {
    var travellersTrigger = travellersPicker.querySelector('.wl-travellers__trigger');
    var travellersPanel = document.getElementById('wl-travellers-panel');
    var travellersDisplay = document.getElementById('wl-travellers-display');
    var travellersValue = document.getElementById('wl-travellers-value');
    var travellersAdults = document.getElementById('wl-travellers-adults');
    var travellersChildren = document.getElementById('wl-travellers-children');
    var travellersDone = travellersPicker.querySelector('.wl-travellers__done');
    var counts = { adults: 1, children: 0 };
    if (travellersAdults && travellersAdults.value) {
      counts.adults = parseInt(travellersAdults.value, 10) || 1;
    }
    if (travellersChildren && travellersChildren.value) {
      counts.children = parseInt(travellersChildren.value, 10) || 0;
    }

    function travellersLabel() {
      var parts = [];
      if (counts.adults > 0) {
        parts.push(counts.adults + (counts.adults === 1 ? ' Adult' : ' Adults'));
      }
      if (counts.children > 0) {
        parts.push(counts.children + (counts.children === 1 ? ' Child' : ' Children'));
      }
      return parts.length ? parts.join(', ') : '1 Adult';
    }

    function syncTravellers() {
      travellersPicker.querySelectorAll('[data-count]').forEach(function (el) {
        var key = el.getAttribute('data-count');
        el.textContent = counts[key];
      });
      travellersPicker.querySelectorAll('.wl-travellers__stepper').forEach(function (stepper) {
        var key = stepper.getAttribute('data-travellers');
        var minus = stepper.querySelector('[data-step="-1"]');
        if (minus) {
          minus.disabled = counts[key] <= (key === 'adults' ? 1 : 0);
        }
      });
      var label = travellersLabel();
      if (travellersDisplay) travellersDisplay.textContent = label;
      if (travellersValue) travellersValue.value = label;
      if (travellersAdults) travellersAdults.value = String(counts.adults);
      if (travellersChildren) travellersChildren.value = String(counts.children);
    }

    function setTravellersOpen(open) {
      travellersPicker.classList.toggle('is-open', open);
      if (travellersTrigger) travellersTrigger.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (travellersPanel) travellersPanel.hidden = !open;
      var searchWrap = travellersPicker.closest('.wl-search-wrap');
      if (searchWrap) {
        searchWrap.classList.toggle('wl-search-travellers-open', open);
      }
    }

    if (travellersTrigger && travellersPanel) {
      travellersTrigger.addEventListener('click', function () {
        setTravellersOpen(!travellersPicker.classList.contains('is-open'));
      });
    }

    travellersPicker.querySelectorAll('.wl-travellers__step').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var stepper = btn.closest('.wl-travellers__stepper');
        if (!stepper) return;
        var key = stepper.getAttribute('data-travellers');
        var step = parseInt(btn.getAttribute('data-step'), 10);
        var min = key === 'adults' ? 1 : 0;
        var max = 9;
        counts[key] = Math.min(max, Math.max(min, counts[key] + step));
        syncTravellers();
      });
    });

    if (travellersDone) {
      travellersDone.addEventListener('click', function () {
        setTravellersOpen(false);
      });
    }

    document.addEventListener('click', function (e) {
      if (!travellersPicker.classList.contains('is-open')) return;
      if (travellersPicker.contains(e.target)) return;
      setTravellersOpen(false);
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && travellersPicker.classList.contains('is-open')) {
        setTravellersOpen(false);
      }
    });

    syncTravellers();
  }

  document.querySelectorAll('.wl-dest-card__fav').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      btn.classList.toggle('is-liked');
    });
  });

  function openDestModal(card) {
    if (!card) return;
    openWlModal(modal, {
      imageEl: modalImage,
      image: card.getAttribute('data-dest-image') || '',
      titleEl: modalTitle,
      title: card.getAttribute('data-dest-title') || '',
      bodyEl: modalBody,
      body: card.getAttribute('data-dest-full') || '',
      linkEl: modalLink,
      link: card.getAttribute('data-dest-link') || '#',
      linkLabel: card.getAttribute('data-dest-link-label') || 'View packages',
      external: card.getAttribute('data-dest-external') === 'true'
    });
  }

  document.querySelectorAll('.wl-dest-explore').forEach(function (btn) {
    btn.addEventListener('click', function () {
      openDestModal(btn.closest('.wl-dest-card'));
    });
  });

  function openLoveModal(card) {
    if (!card) return;
    openWlModal(loveModal, {
      imageEl: loveModalImage,
      image: card.getAttribute('data-love-image') || '',
      titleEl: loveModalTitle,
      title: card.getAttribute('data-love-title') || '',
      bodyEl: loveModalBody,
      body: card.getAttribute('data-love-full') || '',
      linkEl: loveModalLink,
      link: card.getAttribute('data-love-link') || '#',
      linkLabel: card.getAttribute('data-love-link-label') || 'Learn more'
    });
  }

  document.querySelectorAll('.wl-love-explore').forEach(function (btn) {
    btn.addEventListener('click', function () {
      openLoveModal(btn.closest('.wl-love-card'));
    });
  });

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    if (modal && !modal.hidden) closeWlModal(modal);
    if (loveModal && !loveModal.hidden) closeWlModal(loveModal);
    if (partnerModal && !partnerModal.hidden) closeWlModal(partnerModal);
  });

  /* Hero banner carousel — 3s gap, rounded slide transition */
  var heroCarousel = document.getElementById('wl-hero-carousel');
  if (heroCarousel) {
    var slides = heroCarousel.querySelectorAll('.wl-hero');
    var dots = heroCarousel.querySelectorAll('.wl-hero__dot');
    var prevBtn = heroCarousel.querySelector('.wl-hero__arrow--prev');
    var nextBtn = heroCarousel.querySelector('.wl-hero__arrow--next');
    var current = 0;
    var timer = null;
    var delay = parseInt(heroCarousel.getAttribute('data-autoplay') || '3000', 10) || 3000;

    function showSlide(index, forceForward) {
      if (!slides.length) return;
      var previous = current;
      current = (index + slides.length) % slides.length;
      if (previous === current) return;

      var goingForward;
      if (typeof forceForward === 'boolean') {
        goingForward = forceForward;
      } else {
        var forwardDist = (current - previous + slides.length) % slides.length;
        var backwardDist = (previous - current + slides.length) % slides.length;
        goingForward = forwardDist <= backwardDist;
      }

      slides.forEach(function (slide, i) {
        slide.classList.remove('is-active', 'is-prev', 'is-next');
        if (i === current) {
          slide.classList.add('is-active');
          slide.querySelectorAll('.wl-hero__media img, .wl-hero__video').forEach(function (media) {
            media.style.animation = 'none';
            void media.offsetWidth;
            media.style.animation = '';
          });
        } else if (i === previous) {
          slide.classList.add(goingForward ? 'is-prev' : 'is-next');
        } else {
          slide.classList.add(goingForward ? 'is-next' : 'is-prev');
        }
      });
      dots.forEach(function (dot, i) {
        dot.classList.toggle('is-active', i === current);
        dot.setAttribute('aria-selected', i === current ? 'true' : 'false');
      });
      syncHeroTrackHeight();
    }

    function syncHeroTrackHeight() {
      var track = heroCarousel.querySelector('.wl-hero-track');
      var active = heroCarousel.querySelector('.wl-hero.is-active');
      if (!track || !active) return;
      var height = active.offsetHeight;
      if (window.matchMedia('(max-width: 767px)').matches) {
        var mobileMin = Math.round(window.innerHeight * 0.58);
        height = Math.max(height, mobileMin);
      }
      track.style.height = height + 'px';
    }

    slides.forEach(function (slide) {
      slide.querySelectorAll('.wl-hero__media img, .wl-hero__video').forEach(function (media) {
        if (media.tagName === 'IMG' && media.complete) return;
        media.addEventListener('load', function () {
          if (slide.classList.contains('is-active')) {
            syncHeroTrackHeight();
          }
        });
      });
    });

    window.addEventListener('resize', syncHeroTrackHeight);
    syncHeroTrackHeight();

    function nextSlide() { showSlide(current + 1, true); }
    function prevSlide() { showSlide(current - 1, false); }

    function startAutoplay() {
      stopAutoplay();
      if (slides.length > 1) {
        timer = window.setInterval(nextSlide, delay);
      }
    }

    function stopAutoplay() {
      if (timer) {
        window.clearInterval(timer);
        timer = null;
      }
    }

    if (nextBtn) nextBtn.addEventListener('click', function () { nextSlide(); startAutoplay(); });
    if (prevBtn) prevBtn.addEventListener('click', function () { prevSlide(); startAutoplay(); });
    dots.forEach(function (dot) {
      dot.addEventListener('click', function () {
        var idx = parseInt(dot.getAttribute('data-slide-index'), 10);
        if (!isNaN(idx)) {
          showSlide(idx);
          startAutoplay();
        }
      });
    });

    heroCarousel.addEventListener('mouseenter', stopAutoplay);
    heroCarousel.addEventListener('mouseleave', startAutoplay);
    startAutoplay();
  }

  /* Testimonials dual-row marquee — tune speed from content width */
  document.querySelectorAll('[data-marquee]').forEach(function (marquee) {
    marquee.querySelectorAll('.wl-testimonials-marquee__track').forEach(function (track) {
      var half = track.scrollWidth / 2;
      if (half > 0) {
        var seconds = Math.max(28, Math.min(90, half / 42));
        track.style.setProperty('--wl-marquee-duration', seconds + 's');
      }
    });
  });
})();
