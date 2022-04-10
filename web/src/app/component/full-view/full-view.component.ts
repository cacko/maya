import { Component, OnInit } from "@angular/core";
import { ActivatedRoute, Router } from "@angular/router";
import { ApiService } from "../../service/api.service";
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
  loaded = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private photos: ApiService,
    private images: ImageService
  ) {
  }

  ngOnInit(): void {
    this.route.params.subscribe((params) => {
      this.loaded = false;
      this.id = params["id"];
      this.images.startLoader();
      this.images.byId(this.id).then((image) => {
        if (image) {
          const im = new Image();
          im.onload = () => {
            this.image = image;
            this.loaded = true;
            if (image.id) {
              this.images.select(image.id).then(() => {
                this.images.endLoader();
              });
            }
          };
          im.src = image.src;
        }
      });
    });
  }

  async onClose() {
    await this.images.unselect();
  }

  async onPrevious() {
    this.images.startLoader();
    await this.navigate(this.images.previous(this.id));
  }

  async onNext() {
    this.images.startLoader();
    await this.navigate(this.images.next(this.id));
  }

  async navigate(id: string) {
    await this.images.select(id);
  }

}
