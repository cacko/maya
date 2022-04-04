import { Component } from "@angular/core";
import { PhotoEntity } from "./entity/photo";
import { AuthService } from "./service/auth.service";
import { PhotosService } from "./service/photos.service";
import { Image } from "./entity/image";

@Component({
  selector: "web-root",
  templateUrl: "./app.component.html",
  styleUrls: ["./app.component.scss"]
})
export class AppComponent {
  title = "app";
  images: Image[] = [];

  constructor(
    public auth: AuthService,
    public photos: PhotosService
  ) {
    this.auth.isLogged.subscribe(res => {
      if (res) {
        this.photos.photos.subscribe(data => {
          data.forEach((photo) => {
            this.images.push(new Image(photo));
          });
        });
        this.photos.load();
      }
    });
  }


}
