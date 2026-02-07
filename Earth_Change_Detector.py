import ee
ee.Initialize(project="ceremonial-team-472110-i9")

# Bengaluru AOI
aoi = ee.Geometry.Rectangle([77.40, 12.85, 77.80, 13.20])

def mask_s2_clouds(image):
    image = image.select(["B4", "B8", "SCL"])
    
    scl = image.select("SCL")
    mask = (
        scl.neq(3)   # cloud shadow
        .And(scl.neq(8))
        .And(scl.neq(9))
        .And(scl.neq(10))
        .And(scl.neq(11))
    )
    
    return image.updateMask(mask)

before = (
    ee.ImageCollection("COPERNICUS/S2_SR")
    .filterBounds(aoi)
    .filterDate("2017-01-01", "2017-12-31")
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
    .map(mask_s2_clouds)
    .median()
    .clip(aoi)
)

after = (
    ee.ImageCollection("COPERNICUS/S2_SR")
    .filterBounds(aoi)
    .filterDate("2024-01-01", "2024-12-31")
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
    .map(mask_s2_clouds)
    .median()
    .clip(aoi)
)

# NDVI
ndvi_before = before.normalizedDifference(["B8", "B4"])
ndvi_after = after.normalizedDifference(["B8", "B4"])
ndvi_change = ndvi_after.subtract(ndvi_before)

# Stats check
stats = ndvi_change.reduceRegion(
    reducer=ee.Reducer.mean(),
    geometry=aoi,
    scale=10,
    maxPixels=1e9
)

print("Mean NDVI change:", stats.getInfo())
