import { Component } from "@angular/core";
import { PhotoEntity } from "./entity/photo";
import { AuthService } from "./service/auth.service";
import { PhotosService } from "./service/photos.service";
import { ImageEntity } from "./entity/image";
import { GalleryItem, ImageItem } from "ng-gallery";

@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
  styleUrls: ["./app.component.scss"]
})
export class AppComponent {
  title = "app";
  images: GalleryItem[] = [];

  constructor(
    public auth: AuthService,
    public photos: PhotosService
  ) {
    this.auth.isLogged.subscribe(res => {
      if (res) {
        this.photos.photos.subscribe(data => {
          data.forEach((photo) => {
            this.images.push(new ImageItem({
              thumb: `https://cdn.cacko.net/${photo.thumb}`,
              src: `https://cdn.cacko.net/${photo.full}`
            }))
            ;
          });
        });
        this.photos.load();
      }
    });
  }


}
