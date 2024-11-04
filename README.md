# Generate CityJSON

This is a small side quest to try and convert local climate zone (LCZ) raster maps to CityJSON in order to render them in 3D.

- Run the script with `python3 generator.py`.
- Validate by uploading `test.city.json` to https://validator.cityjson.org/
- Render in Ninja web viewer: https://ninja.cityjson.org/#
- Compare to [3dbag viewer](https://3dbag.nl/en/viewer?rdx=125691.20342463444&rdy=485509.3760868434&ox=-1829.5717134937004&oy=2303.2675256783377&oz=-1508.918937586117&placeMarker=true)

So far I'm able to reproduce (to some extent) the prototypes from [paper](https://www.sciencedirect.com/science/article/abs/pii/S0034425723001244):

Reference             |  Reproduced in CityJSON
:-------------------------:|:-------------------------:
![Reference](LCZ_prototypes_original.jpg) | ![Reproduced version](LCZ_prototypes_reproduced_in_cityjson.png)
![google earth amsterdam](https://github.com/user-attachments/assets/eadcf5af-a186-457c-bfbe-d16f14e716e2) | ![cityjson lcz amsterdam](https://github.com/user-attachments/assets/33984464-1aaf-4808-a7ea-b7e290bef8f3)
![google earth](https://github.com/user-attachments/assets/eadcf5af-a186-457c-bfbe-d16f14e716e2) | ![cityjson lcz](https://github.com/user-attachments/assets/33984464-1aaf-4808-a7ea-b7e290bef8f3)
![manhattan google earth](https://github.com/user-attachments/assets/3e97afcb-e88a-42b8-bc2b-c110e88ed6b9) | ![manhattan cityjson lcz](https://github.com/user-attachments/assets/ceec818a-a3ec-41e9-adba-23f858c2ee4d)