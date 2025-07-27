# Suppliers Page Testing Checklist

## Before Adding API Key (Demo Mode)

### ✅ Basic Page Load
- [ ] Page loads without errors
- [ ] Hero section displays correctly
- [ ] Search form is visible
- [ ] State dropdown is populated with Indian states
- [ ] Category buttons are clickable

### ✅ Demo Search Functionality
- [ ] Click "Test Search" button
- [ ] Loading spinner appears
- [ ] Demo suppliers appear (3 suppliers)
- [ ] Each supplier card shows:
  - [ ] Supplier name
  - [ ] Address
  - [ ] Phone number
  - [ ] Rating
  - [ ] "View Products" button

### ✅ Product Functionality
- [ ] Click "View Products" on any supplier
- [ ] Products section expands
- [ ] Product tiles show:
  - [ ] Product name
  - [ ] Price
  - [ ] Rating
  - [ ] Quantity controls
  - [ ] Add to cart button

### ✅ Cart Integration
- [ ] Click "Add" button on any product
- [ ] Cart notification appears
- [ ] Product is added to cart
- [ ] Cart count updates in navbar

### ✅ Location Features
- [ ] Select a state from dropdown
- [ ] Notification appears confirming location set
- [ ] Click "Use Current Location" button
- [ ] Browser asks for location permission

## After Adding API Key (Full Functionality)

### ✅ Google Maps Integration
- [ ] No "Google is not defined" errors in console
- [ ] Places service initializes successfully
- [ ] Console shows "Google Maps API loaded"
- [ ] Console shows "Google Places service initialized"

### ✅ Real Search Functionality
- [ ] Select a state (e.g., "Maharashtra")
- [ ] Enter search term (e.g., "vegetables")
- [ ] Click "Find Suppliers"
- [ ] Real suppliers from Google Places appear
- [ ] Suppliers show real addresses and ratings

### ✅ Category Search
- [ ] Click any category button (e.g., "Vegetables")
- [ ] Search input updates with category name
- [ ] Click "Find Suppliers"
- [ ] Results are relevant to category

### ✅ Current Location
- [ ] Click "Use Current Location"
- [ ] Allow location access
- [ ] Location is detected and set
- [ ] Search works with current location

## Error Handling Tests

### ✅ No Internet Connection
- [ ] Disconnect internet
- [ ] Try to search
- [ ] Fallback demo data appears
- [ ] Notification shows "Using demo data"

### ✅ Invalid API Key
- [ ] Use invalid API key
- [ ] Try to search
- [ ] Fallback demo data appears
- [ ] No JavaScript errors

### ✅ Location Denied
- [ ] Deny location permission
- [ ] Error notification appears
- [ ] Can still use state selection

## Performance Tests

### ✅ Loading Speed
- [ ] Page loads in under 3 seconds
- [ ] Search results appear in under 5 seconds
- [ ] No memory leaks in console

### ✅ Mobile Responsiveness
- [ ] Test on mobile device/emulator
- [ ] All buttons are clickable
- [ ] Text is readable
- [ ] Notifications fit screen

## Console Checks

### ✅ No Errors
- [ ] No red errors in browser console
- [ ] Only expected log messages appear
- [ ] No 404 errors for missing files

### ✅ Expected Log Messages
- [ ] "Google Maps API loaded"
- [ ] "Google Places service initialized"
- [ ] "Cart initialized"
- [ ] "Database tables created successfully"

## Browser Compatibility

### ✅ Chrome
- [ ] All features work
- [ ] No console errors

### ✅ Firefox
- [ ] All features work
- [ ] No console errors

### ✅ Safari
- [ ] All features work
- [ ] No console errors

### ✅ Edge
- [ ] All features work
- [ ] No console errors

## Common Issues & Solutions

### Issue: "Google is not defined"
**Solution:** Check API key and internet connection

### Issue: No search results
**Solution:** Verify Places API is enabled in Google Cloud Console

### Issue: Cart not working
**Solution:** Check if cart.js and database.js are loading

### Issue: Location not working
**Solution:** Ensure HTTPS and location permissions

### Issue: Styles look broken
**Solution:** Check if suppliers.css is loading correctly

## Success Criteria

✅ **Page is ready when:**
- All demo features work without API key
- Real search works with valid API key
- Cart integration functions properly
- Mobile responsive design works
- No console errors
- Fallback systems work when API fails

Your suppliers page should now be fully functional with Google Maps integration!