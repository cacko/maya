import { Component } from "@angular/core";
import { AuthService } from "./service/auth.service";
import { PhotosService } from "./service/photos.service";
import { Image } from "./entity/image";
import { SwUpdate } from "@angular/service-worker";
import { MatSnackBar } from "@angular/material/snack-bar";
import { interval } from "rxjs";

@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
  styleUrls: ["./app.component.scss"]
})
export class AppComponent {
  title = "app";
  images: Image[] = [];
  page = 1;
  loading: boolean = true;
  updating = true;

  constructor(
    public auth: AuthService,
    public photos: PhotosService,
    private swUpdate: SwUpdate,
    private snackBar: MatSnackBar
  ) {
    if (this.swUpdate.isEnabled) {
      this.swUpdate.available.subscribe((evt) => {
        this.updating = true;
        this.snackBar
          .open("Update is available", "Update")
          .onAction()
          .subscribe(() =>
            this.swUpdate
              .activateUpdate()
              .then(() => document.location.reload())
          );
      });
      interval(10000).subscribe(() => {
        this.swUpdate.checkForUpdate();
      });
    }
    this.auth.isLogged.subscribe(res => {
      if (res) {
        this.photos.photos.subscribe(data => {
          data.forEach((photo) => {
            this.images.push(new Image(photo));
          });
          this.loading = false;
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
