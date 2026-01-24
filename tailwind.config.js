/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './layouts/**/*.html',
    './content/**/*.{html,md}',
    './static/js/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        // Primary - Forest Green
        'forest': {
          50: '#f0f7f1',
          100: '#dceee0',
          200: '#bcdcc4',
          300: '#91c39d',
          400: '#66a572',
          500: '#2C5F2D',  // Main brand color
          600: '#244e25',
          700: '#1d3f1e',
          800: '#1A3A1B',  // Deep forest
          900: '#142814',
        },

        // Accent - Sage
        'sage': {
          50: '#f7faf4',
          100: '#eef5e8',
          200: '#dcebd1',
          300: '#c5deb5',
          400: '#aecf99',
          500: '#97BC62',  // Light accent
          600: '#7fa750',
          700: '#678841',
          800: '#516d35',
          900: '#425a2c',
        },

        // Earth Tones
        'terracotta': {
          50: '#fdf5f3',
          100: '#fae8e4',
          200: '#f5d1c9',
          300: '#edb3a5',
          400: '#e38c77',
          500: '#C97064',  // Warm accent
          600: '#b5564a',
          700: '#96453c',
          800: '#7d3c34',
          900: '#6a352f',
        },

        'sand': '#E8D5B7',
        'stone': '#8B7E74',
        'clay': '#B4846C',
        'charcoal': '#2D2D2D',
        'warm-white': '#FAF8F3',
        'cream': '#F5F1E8',
      },

      fontFamily: {
        'serif': ['Playfair Display', 'Georgia', 'serif'],
        'sans': ['Inter', 'system-ui', 'sans-serif'],
      },

      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
        '5xl': ['3rem', { lineHeight: '1' }],
        '6xl': ['3.75rem', { lineHeight: '1' }],
      },

      spacing: {
        '128': '32rem',
        '144': '36rem',
      },

      borderRadius: {
        '4xl': '2rem',
      },

      boxShadow: {
        'soft': '0 2px 15px -3px rgba(0, 0, 0, 0.07), 0 10px 20px -2px rgba(0, 0, 0, 0.04)',
        'medium': '0 4px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 30px -5px rgba(0, 0, 0, 0.08)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
  ],
}
