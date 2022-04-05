import { Component, OnInit } from "@angular/core";
import { ActivatedRoute, Router } from "@angular/router";
import { PhotosService } from "../../service/photos.service";
import { Photo } from "../../entity/photo";
import { ImageService } from "../../service/image.service";

@Component({
  selector: "app-full-view",
  templateUrl: "./full-view.component.html",
  styleUrls: ["./full-view.component.scss"]
})
export class FullViewComponent implements OnInit {

  id: string = "";
  image: Photo | undefined | null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private photos: PhotosService,
    private images: ImageService
  ) {
  }

  ngOnInit(): void {
    this.route.params.subscribe((params) => {
      setTimeout(() => {
        this.images.startLoader();
      },0);
      this.id = params["id"];
      this.images.byId(this.id).then((image) => {
        const im = new Image();
        im.onload = () => {
          this.image = image;
          this.photos.expand(this.id);
        };
        if (image) {
          im.src = image.src;
        }
      });
    });
  }

  style(): { [key: string]: string } {
    return {
      "background-image": `url("${this.image?.src}")`,
      "background-size": "contain"
    };
  }

  onClose() {
    this.photos.shrink();
  }

}
