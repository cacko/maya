import { Component } from "@angular/core";
import { AuthService } from "./service/auth.service";
import { PhotosService } from "./service/photos.service";
import { Image } from "./entity/image";

@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
  styleUrls: ["./app.component.scss"],
})
export class AppComponent {
  title = "app";
  images: Image[] = [];
  page = 1;

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

  onScrollDown() {
    console.log("goiong down");
    this.photos.load(++this.page);
  }

  onScrollUp() {
    console.log("goiong down");

  }
}
