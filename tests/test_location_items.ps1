$base = "http://127.0.0.1:8000"

# 1. Utwórz lokację
$location = Invoke-RestMethod -Uri "$base/locations" -Method Post -Body '{"name":"Test Fridge"}' -ContentType "application/json"
Write-Host "Created location: $($location.id) - $($location.name)"

# 2. Utwórz produkt
$product = Invoke-RestMethod -Uri "$base/products" -Method Post -Body '{"name":"Test Milk","brand":"Test"}' -ContentType "application/json"
Write-Host "Created product: $($product.id) - $($product.name)"

# 3. Utwórz sklep
$store = Invoke-RestMethod -Uri "$base/stores" -Method Post -Body '{"name":"Test Store"}' -ContentType "application/json"
Write-Host "Created store: $($store.id) - $($store.name)"

# 4. Dodaj item do lokacji
$item = @{
    product_id = $product.id
    location_id = $location.id
    store_id = $store.id
    quantity = 1.5
    price = 9.99
} | ConvertTo-Json

$newItem = Invoke-RestMethod -Uri "$base/inventory_items" -Method Post -Body $item -ContentType "application/json"
Write-Host "Created inventory item: $($newItem.id)"

# 5. Testuj nowy endpoint
Write-Host "`nTesting GET /locations/$($location.id)/items..."
$result = Invoke-RestMethod -Uri "$base/locations/$($location.id)/items" -Method Get
Write-Host "Total items: $($result.total)"
$result | ConvertTo-Json -Depth 10