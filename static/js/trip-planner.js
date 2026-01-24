/**
 * Trip Planner Store - Alpine.js
 * Manages trip planning state, calculations, and persistence
 */

console.log('🚀 Trip Planner JS loaded at', new Date().toISOString());

// Global singleton to prevent duplicate stores
if (window._tripPlannerStoreCreated) {
  console.warn('⚠️ Trip Planner store already created, skipping script');
} else {
  window._tripPlannerStoreCreated = true;

  document.addEventListener('alpine:init', () => {
    console.log('✅ Alpine init - Creating tripPlanner store');

    Alpine.store('tripPlanner', {
      // State
      isOpen: false,
      currentTrip: null,
    sites: [],

    // Trip metadata
    tripName: 'My Heritage Trip',
    startDate: null,
    transportMode: 'car', // car, train, mixed
    budgetLevel: 'mid', // budget, mid, luxury

    // Calculations cache
    totalDistance: 0,
    totalDuration: 0,
    totalBudget: 0,

    // Guard flag to prevent duplicate additions
    _addingSite: false,

    // Initialize
    init() {
      this.loadFromStorage();
      console.log('Trip Planner initialized, sites:', this.sites.length);
      console.log('Sites IDs:', this.sites.map(s => s.id));
    },

    // Add site to trip
    addSite(site) {
      try {
        console.log('[addSite] ===== START =====');
        console.log('[addSite] Site to add:', site.id, '-', site.title);
        console.log('[addSite] Current sites count:', this.sites.length);
        console.log('[addSite] Current sites IDs:', JSON.stringify(this.sites.map(s => s.id)));
        console.log('[addSite] Guard flag _addingSite:', this._addingSite);

        // Guard against rapid double-clicks
        if (this._addingSite) {
          console.warn('[addSite] BLOCKED: Already adding a site, ignoring duplicate call');
          return;
        }

        this._addingSite = true;

        // Check if already added (use hasSite for consistency)
        if (this.hasSite(site.id)) {
          console.log('[addSite] Site already exists, opening sidebar');
          this.showToast('Site already in your trip', 'info');
          this.open();
          this._addingSite = false;
          return;
        }

        console.log('[addSite] Pushing to sites array...');
        // Add site
        this.sites.push({
          id: site.id,
          title: site.title,
          slug: site.slug,
          image: site.image || '',
          location: site.location || '',
          coordinates: site.coordinates || { lat: 0, lng: 0 },
          visitDuration: site.visitDuration || 2, // hours
          entryFee: site.entryFee || 0,
          order: this.sites.length + 1,
          notes: ''
        });
        console.log('[addSite] Sites array now has', this.sites.length, 'items');

        // Open sidebar if closed
        console.log('[addSite] Opening sidebar...');
        if (!this.isOpen) {
          this.open();
        }
        console.log('[addSite] Sidebar isOpen:', this.isOpen);

        // Recalculate
        console.log('[addSite] Calculating...');
        this.calculate();

        // Save
        console.log('[addSite] Saving to storage...');
        this.saveToStorage();

        // Show toast
        console.log('[addSite] Showing toast...');
        this.showToast(`Added ${site.title} to your trip`, 'success');

        console.log('[addSite] SUCCESS! Added site:', site.title);
        console.log('[addSite] Final sites count:', this.sites.length);
        console.log('[addSite] Final sites IDs:', JSON.stringify(this.sites.map(s => s.id)));
        console.log('[addSite] ===== END =====');
      } catch (error) {
        console.error('[addSite] ERROR:', error);
        alert('Error adding site: ' + error.message);
      } finally {
        // Always reset guard flag
        this._addingSite = false;
        console.log('[addSite] Guard flag reset');
      }
    },

    // Remove site from trip
    removeSite(siteId) {
      console.log('[removeSite] ===== START =====');
      console.log('[removeSite] Attempting to remove siteId:', siteId);
      console.log('[removeSite] Current sites array:', JSON.stringify(this.sites));
      console.log('[removeSite] Sites count BEFORE:', this.sites.length);

      const beforeLength = this.sites.length;
      this.sites = this.sites.filter(s => {
        console.log('[removeSite] Checking site:', s.id, 'against:', siteId, 'match:', s.id === siteId);
        return s.id !== siteId;
      });

      console.log('[removeSite] Sites count AFTER:', this.sites.length);
      console.log('[removeSite] Sites removed:', beforeLength - this.sites.length);

      // Reorder
      this.sites.forEach((site, index) => {
        site.order = index + 1;
      });

      console.log('[removeSite] Recalculating...');
      this.calculate();

      console.log('[removeSite] Saving to storage...');
      this.saveToStorage();

      // Update FAB badge
      this.updateFABBadge();

      // Hide FAB if no sites left
      if (this.sites.length === 0 && !this.isOpen) {
        const fab = document.getElementById('tripPlannerFAB');
        if (fab) {
          fab.style.display = 'none';
        }
      }

      console.log('[removeSite] Showing toast...');
      this.showToast('Site removed from trip', 'info');

      console.log('[removeSite] ===== END =====');
    },

    // Check if site is in trip
    hasSite(siteId) {
      return this.sites.some(s => s.id === siteId);
    },

    // Clear all sites
    clearTrip() {
      if (confirm('Remove all sites from your trip?')) {
        this.sites = [];
        this.tripName = 'My Heritage Trip';
        this.totalDistance = 0;
        this.totalDuration = 0;
        this.totalBudget = 0;
        this.saveToStorage();
        this.showToast('Trip cleared', 'info');

        // Hide FAB when no sites
        const fab = document.getElementById('tripPlannerFAB');
        if (fab) {
          fab.style.display = 'none';
        }
      }
    },

    // Toggle sidebar
    toggle() {
      this.isOpen = !this.isOpen;
    },

    open() {
      console.log('[OPEN] Opening sidebar, current isOpen:', this.isOpen);
      this.isOpen = true;
      console.log('[OPEN] After setting, isOpen:', this.isOpen);

      // Hide floating button
      const fab = document.getElementById('tripPlannerFAB');
      if (fab) {
        console.log('[OPEN] Hiding FAB');
        fab.style.display = 'none';
      }

      // FORCE DOM UPDATE with pure CSS (no Tailwind classes)
      const sidebar = document.getElementById('tripPlannerSidebar');
      if (sidebar) {
        console.log('[OPEN] Found sidebar element');
        sidebar.style.display = 'flex';
        sidebar.style.right = '-400px'; // Start off screen
        console.log('[OPEN] Set display flex, right -400px');

        setTimeout(() => {
          sidebar.style.transition = 'right 300ms ease-out';
          sidebar.style.right = '0px';
          console.log('[OPEN] Animating to right 0px');
        }, 50);
      } else {
        console.error('[OPEN] Sidebar element NOT FOUND in DOM!');
      }
    },

    close() {
      console.log('[CLOSE] Closing sidebar');
      this.isOpen = false;

      const sidebar = document.getElementById('tripPlannerSidebar');
      if (sidebar) {
        sidebar.style.right = '-400px';
        setTimeout(() => {
          sidebar.style.display = 'none';

          // Show floating button if there are sites
          if (this.sites.length > 0) {
            const fab = document.getElementById('tripPlannerFAB');
            if (fab) {
              console.log('[CLOSE] Showing FAB, sites:', this.sites.length);
              fab.style.display = 'flex';
              this.updateFABBadge();
            }
          }
        }, 300);
      }
    },

    // Update floating button badge
    updateFABBadge() {
      const badge = document.getElementById('tripPlannerFABBadge');
      if (badge) {
        const span = badge.querySelector('span');
        if (span) {
          span.textContent = this.sites.length;
          console.log('[updateFABBadge] Updated badge to:', this.sites.length);
        }
      }
    },

    // Reorder sites (drag and drop)
    reorder(oldIndex, newIndex) {
      const site = this.sites.splice(oldIndex, 1)[0];
      this.sites.splice(newIndex, 0, site);

      // Update order numbers
      this.sites.forEach((site, index) => {
        site.order = index + 1;
      });

      this.calculate();
      this.saveToStorage();
    },

    // Calculate total distance
    calculateDistance() {
      if (this.sites.length < 2) {
        this.totalDistance = 0;
        return 0;
      }

      let distance = 0;

      for (let i = 0; i < this.sites.length - 1; i++) {
        const from = this.sites[i].coordinates;
        const to = this.sites[i + 1].coordinates;
        distance += this.haversineDistance(from.lat, from.lng, to.lat, to.lng);
      }

      // Account for road routing (multiply by 1.3)
      if (this.transportMode === 'car') {
        distance = distance * 1.3;
      } else if (this.transportMode === 'train') {
        distance = distance * 1.2;
      }

      this.totalDistance = Math.round(distance);
      return this.totalDistance;
    },

    // Haversine formula for distance between two coordinates
    haversineDistance(lat1, lon1, lat2, lon2) {
      const R = 6371; // Earth's radius in km
      const dLat = this.toRad(lat2 - lat1);
      const dLon = this.toRad(lon2 - lon1);

      const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(this.toRad(lat1)) * Math.cos(this.toRad(lat2)) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2);

      const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
      const distance = R * c;

      return distance;
    },

    toRad(degrees) {
      return degrees * (Math.PI / 180);
    },

    // Calculate total duration
    calculateDuration() {
      if (this.sites.length === 0) {
        this.totalDuration = 0;
        return 0;
      }

      // Sum visit durations
      let duration = this.sites.reduce((sum, site) => sum + site.visitDuration, 0);

      // Add travel time (estimate 1 hour per 80km)
      if (this.sites.length > 1) {
        const travelTime = this.totalDistance / 80;
        duration += travelTime;
      }

      // Add buffer time (30 min per site)
      duration += this.sites.length * 0.5;

      this.totalDuration = Math.round(duration * 10) / 10; // Round to 1 decimal
      return this.totalDuration;
    },

    // Calculate total budget
    calculateBudget() {
      if (this.sites.length === 0) {
        this.totalBudget = 0;
        return 0;
      }

      let budget = 0;

      // Entrance fees
      budget += this.sites.reduce((sum, site) => sum + (site.entryFee || 10), 0);

      // Transportation
      if (this.transportMode === 'car') {
        budget += this.totalDistance * 0.15; // €0.15/km
      } else if (this.transportMode === 'train') {
        budget += this.totalDistance * 0.20; // €0.20/km
      }

      // Accommodation (based on days needed)
      const days = Math.ceil(this.totalDuration / 8);
      const nights = Math.max(0, days - 1);
      const accommodationRates = { budget: 50, mid: 80, luxury: 150 };
      budget += nights * accommodationRates[this.budgetLevel];

      // Food
      const foodRates = { budget: 30, mid: 50, luxury: 80 };
      budget += days * foodRates[this.budgetLevel];

      this.totalBudget = Math.round(budget);
      return this.totalBudget;
    },

    // Run all calculations
    calculate() {
      this.calculateDistance();
      this.calculateDuration();
      this.calculateBudget();
    },

    // Get days needed
    getDaysNeeded() {
      return Math.ceil(this.totalDuration / 8);
    },

    // Generate day-by-day itinerary
    getDayByDayItinerary() {
      if (this.sites.length === 0) return [];

      const days = [];
      let currentDay = { number: 1, sites: [], totalHours: 0 };
      const maxHoursPerDay = 8;

      this.sites.forEach((site, index) => {
        // Calculate travel time to this site from previous site
        let travelTime = 0;
        if (index > 0 && currentDay.sites.length > 0) {
          const prevSite = currentDay.sites[currentDay.sites.length - 1];
          const distance = this.haversineDistance(
            prevSite.coordinates.lat,
            prevSite.coordinates.lng,
            site.coordinates.lat,
            site.coordinates.lng
          );
          travelTime = (distance * (this.transportMode === 'car' ? 1.3 : 1.2)) / 80; // hours
        }

        const siteTimeNeeded = site.visitDuration + travelTime + 0.5; // visit + travel + buffer

        // Check if adding this site exceeds day limit
        if (currentDay.sites.length > 0 && currentDay.totalHours + siteTimeNeeded > maxHoursPerDay) {
          // Start new day
          days.push(currentDay);
          currentDay = { number: days.length + 1, sites: [], totalHours: 0 };
        }

        // Add site to current day
        currentDay.sites.push({
          ...site,
          travelTime: Math.round(travelTime * 60), // minutes
          order: currentDay.sites.length + 1
        });
        currentDay.totalHours += siteTimeNeeded;
      });

      // Add the last day
      if (currentDay.sites.length > 0) {
        days.push(currentDay);
      }

      return days;
    },

    // Optimize route (nearest neighbor algorithm)
    optimizeRoute() {
      console.log('[optimizeRoute] Starting optimization, sites:', this.sites.length);

      if (this.sites.length < 3) {
        console.log('[optimizeRoute] Not enough sites (need 3+), showing warning');
        this.showToast('Add at least 3 sites to optimize', 'warning');
        return;
      }

      const beforeDistance = this.totalDistance;
      console.log('[optimizeRoute] Distance before:', beforeDistance);

      // Keep first site as start
      const start = this.sites[0];
      const remaining = this.sites.slice(1);
      const optimized = [start];

      // Nearest neighbor algorithm
      while (remaining.length > 0) {
        const current = optimized[optimized.length - 1];
        let nearest = null;
        let minDistance = Infinity;

        remaining.forEach(site => {
          const distance = this.haversineDistance(
            current.coordinates.lat,
            current.coordinates.lng,
            site.coordinates.lat,
            site.coordinates.lng
          );

          if (distance < minDistance) {
            minDistance = distance;
            nearest = site;
          }
        });

        if (nearest) {
          optimized.push(nearest);
          remaining.splice(remaining.indexOf(nearest), 1);
        }
      }

      // Update sites with optimized order
      this.sites = optimized;
      this.sites.forEach((site, index) => {
        site.order = index + 1;
      });

      this.calculate();
      this.saveToStorage();

      const afterDistance = this.totalDistance;
      const saved = beforeDistance - afterDistance;

      if (saved > 0) {
        this.showToast(`Optimized! Saved ${Math.round(saved)} km`, 'success');
      } else {
        this.showToast('Route already optimal', 'info');
      }
    },

    // Save to localStorage
    saveToStorage() {
      const data = {
        tripName: this.tripName,
        startDate: this.startDate,
        transportMode: this.transportMode,
        budgetLevel: this.budgetLevel,
        sites: this.sites,
        totalDistance: this.totalDistance,
        totalDuration: this.totalDuration,
        totalBudget: this.totalBudget,
        savedAt: new Date().toISOString()
      };

      try {
        localStorage.setItem('currentTrip', JSON.stringify(data));
        console.log('Trip saved to localStorage');
      } catch (e) {
        console.error('Failed to save trip:', e);
      }
    },

    // Load from localStorage
    loadFromStorage() {
      try {
        const data = localStorage.getItem('currentTrip');
        if (data) {
          const trip = JSON.parse(data);
          this.tripName = trip.tripName || 'My Heritage Trip';
          this.startDate = trip.startDate;
          this.transportMode = trip.transportMode || 'car';
          this.budgetLevel = trip.budgetLevel || 'mid';
          this.sites = trip.sites || [];
          this.totalDistance = trip.totalDistance || 0;
          this.totalDuration = trip.totalDuration || 0;
          this.totalBudget = trip.totalBudget || 0;

          console.log('Trip loaded from localStorage:', this.sites.length, 'sites');
        }
      } catch (e) {
        console.error('Failed to load trip:', e);
      }
    },

    // Export trip data for sharing
    exportForSharing() {
      const data = {
        name: this.tripName,
        sites: this.sites.map(s => ({
          id: s.id,
          slug: s.slug,
          order: s.order
        })),
        transport: this.transportMode,
        budget: this.budgetLevel
      };

      // Base64 encode
      const json = JSON.stringify(data);
      const encoded = btoa(unescape(encodeURIComponent(json)));

      return encoded;
    },

    // Import trip from shared data
    importFromSharing(encoded) {
      try {
        const json = decodeURIComponent(escape(atob(encoded)));
        const data = JSON.parse(json);

        // Would need to fetch full site data from slugs
        // For now, just show success
        this.showToast('Trip loaded successfully', 'success');

        return data;
      } catch (e) {
        console.error('Failed to import trip:', e);
        this.showToast('Invalid trip data', 'error');
        return null;
      }
    },

    // Open map view
    openMap() {
      console.log('[openMap] Starting, sites:', this.sites.length);

      if (this.sites.length === 0) {
        console.log('[openMap] No sites, showing warning');
        this.showToast('Add sites to your trip first', 'warning');
        return;
      }

      // Dispatch event to open modal
      console.log('[openMap] Dispatching open-map event');
      window.dispatchEvent(new CustomEvent('open-map'));

      // Wait for modal animation to complete, then initialize map
      console.log('[openMap] Scheduling map initialization in 400ms');
      setTimeout(() => {
        console.log('[openMap] Timeout reached, calling initializeMap()');
        this.initializeMap();
      }, 400);
    },

    // Initialize Leaflet map
    initializeMap() {
      console.log('[initializeMap] Starting...');

      // Clear existing map if any
      const mapContainer = document.getElementById('tripMap');
      if (!mapContainer) {
        console.error('[initializeMap] ERROR: Map container #tripMap not found in DOM!');
        return;
      }

      console.log('[initializeMap] Found map container:', mapContainer);
      console.log('[initializeMap] Container visibility:', window.getComputedStyle(mapContainer).display);
      console.log('[initializeMap] Container dimensions:', mapContainer.offsetWidth, 'x', mapContainer.offsetHeight);

      // Check if container is visible
      if (mapContainer.offsetWidth === 0 || mapContainer.offsetHeight === 0) {
        console.error('[initializeMap] ERROR: Map container has zero dimensions! Modal might not be open yet.');
        this.showToast('Please wait, opening map...', 'info');
        setTimeout(() => this.initializeMap(), 200);
        return;
      }

      // Remove existing map instance completely
      if (this._mapInstance) {
        console.log('[initializeMap] Removing existing map instance');
        this._mapInstance.remove();
        this._mapInstance = null;
      }

      // Clear container and reset Leaflet state
      mapContainer.innerHTML = '';
      mapContainer._leaflet_id = null; // Force Leaflet to treat as new container

      // Calculate center point
      const avgLat = this.sites.reduce((sum, site) => sum + site.coordinates.lat, 0) / this.sites.length;
      const avgLng = this.sites.reduce((sum, site) => sum + site.coordinates.lng, 0) / this.sites.length;
      console.log('[initializeMap] Map center:', avgLat, avgLng);

      // Check if Leaflet is loaded
      if (typeof L === 'undefined') {
        console.error('[initializeMap] ERROR: Leaflet.js not loaded!');
        this.showToast('Map library not loaded', 'error');
        return;
      }

      // Initialize map
      console.log('[initializeMap] Creating Leaflet map...');
      const map = L.map('tripMap').setView([avgLat, avgLng], 7);
      this._mapInstance = map; // Store reference for cleanup
      console.log('[initializeMap] Map created successfully');

      // Add tile layer
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
      }).addTo(map);

      // Add markers for each site
      const markers = [];
      this.sites.forEach((site, index) => {
        const marker = L.marker([site.coordinates.lat, site.coordinates.lng])
          .addTo(map)
          .bindPopup(`
            <div class="p-2">
              <div class="font-bold text-forest-700 mb-1">${index + 1}. ${site.title}</div>
              <div class="text-sm text-stone">
                ${site.visitDuration}h visit • €${site.entryFee || 0}
              </div>
            </div>
          `);

        markers.push(marker);
      });

      // Draw route line
      if (this.sites.length > 1) {
        const routeCoords = this.sites.map(site => [site.coordinates.lat, site.coordinates.lng]);
        L.polyline(routeCoords, {
          color: '#2D5016',
          weight: 3,
          opacity: 0.7,
          dashArray: '10, 10'
        }).addTo(map);
      }

      // Fit bounds to show all markers
      const bounds = L.latLngBounds(this.sites.map(site => [site.coordinates.lat, site.coordinates.lng]));
      map.fitBounds(bounds, { padding: [50, 50] });
    },

    // Show toast notification
    showToast(message, type = 'info') {
      // Simple toast implementation
      const toast = document.createElement('div');
      toast.className = `fixed top-20 right-4 z-50 px-6 py-3 rounded-lg shadow-lg text-white transform transition-all duration-300 translate-x-0`;

      const colors = {
        success: 'bg-green-600',
        error: 'bg-red-600',
        warning: 'bg-yellow-600',
        info: 'bg-forest-600'
      };

      toast.classList.add(colors[type] || colors.info);
      toast.textContent = message;

      document.body.appendChild(toast);

      // Fade in
      setTimeout(() => {
        toast.style.transform = 'translateX(0)';
      }, 10);

      // Remove after 3 seconds
      setTimeout(() => {
        toast.style.transform = 'translateX(400px)';
        setTimeout(() => {
          document.body.removeChild(toast);
        }, 300);
      }, 3000);
    }
  });
});
} // End of if (!window._tripPlannerStoreCreated)
