import { Component, HostListener, OnInit } from "@angular/core";
import { AuthService } from "./service/auth.service";
import { PhotosService } from "./service/photos.service";
import { SwUpdate } from "@angular/service-worker";
import { MatSnackBar } from "@angular/material/snack-bar";
import { interval } from "rxjs";
import { ImageService } from "./service/image.service";
import { Router } from "@angular/router";

@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
  styleUrls: ["./app.component.scss"]
})
export class AppComponent implements OnInit {
  title = "app";
  page = 1;
  loading: boolean = true;
  updating = true;
  selected: string | undefined | null = null;

  throttle = 50;
  scrollDistance = 2;
  scrollUpDistance = 1.5;

  constructor(
    public auth: AuthService,
    public photos: PhotosService,
    public imageService: ImageService,
    private swUpdate: SwUpdate,
    private snackBar: MatSnackBar,
    private router: Router
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
          this.imageService.append(data);
          this.loading = false;
        });
        this.photos.load();
      }
    });
  }

  ngOnInit(): void {
    this.selected = null;
    this.photos.photo.subscribe((selected) => {
      setTimeout(() => {
        this.selected = selected;
      }, 0);
    });
  }

  onScrollDown() {
    console.log("goiong down");
    this.photos.load(++this.page);
  }

  @HostListener("document:keydown.escape", ["$event"])
  onEscape() {
    if (this.selected) {
      this.router.navigate(["/"], { preserveFragment: true });
      this.photos.shrink();
    }
  }
}
