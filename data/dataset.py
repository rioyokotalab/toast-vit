import os,json
import numpy as np
import torch
import torchvision
from torchvision.datasets.folder import ImageFolder, default_loader

from torch.utils.data.dataset import Subset
from torchvision import transforms
from data.cutout import Cutout
from data.autoaugment import CIFAR10Policy

class Dataset(object):
    def __init__(self, args):
        # Data Loader (Input Pipeline)
        self.train_loader = torch.utils.data.DataLoader(dataset=self.train_dataset,
                                                    batch_size=args.batch_size,
                                                    shuffle=args.dataset_shuffle,
                                                    pin_memory=True,
                                                    num_workers=args.num_workers)
        self.train_val_loader = torch.utils.data.DataLoader(dataset=self.train_val_dataset,
                                                    batch_size=args.val_batch_size,
                                                    shuffle=False,
                                                    pin_memory=True,
                                                    num_workers=args.num_workers)
        self.val_loader = torch.utils.data.DataLoader(dataset=self.val_dataset,
                                                    batch_size=args.val_batch_size,
                                                    shuffle=False,
                                                    pin_memory=True,
                                                    num_workers=args.num_workers)

        self.num_steps_per_epoch = len(self.train_loader)


    def create_transform(self,args):
        self.train_transform = transforms.Compose([])
        self.val_transform = transforms.Compose([])
        normalize = transforms.Normalize(   mean=[x / 255.0 for x in [125.3, 123.0, 113.9]],
                                            std=[x / 255.0 for x in [63.0, 62.1, 66.7]])
        
        self.train_transform.transforms.append(transforms.RandomCrop(32, padding=4))
        self.val_transform.transforms.append(transforms.Resize((32, 32)))
        self.train_transform.transforms.append(transforms.RandomHorizontalFlip())
        self.train_transform.transforms.append(CIFAR10Policy())
        self.train_transform.transforms.append(transforms.ToTensor())
        self.train_transform.transforms.append(normalize)

        self.val_transform.transforms.append(transforms.ToTensor())
        self.val_transform.transforms.append(normalize)

class MNIST(Dataset):
    def __init__(self, args):
        self.num_classes = 10
        self.num_channels=1
        self.img_size = 28

        self.train_transform = transforms.Compose([])
        self.train_transform.transforms.append(transforms.ToTensor())
        self.train_transform.transforms.append(transforms.Normalize((0.1307,), (0.3081,)))
        self.val_transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))])

        self.train_dataset = torchvision.datasets.MNIST(root='data/',
                                            train=True,
                                            download=True,
                                            transform=self.train_transform,)
        self.train_val_dataset = torchvision.datasets.MNIST(root='data/',
                                            train=True,
                                            download=True,
                                            transform=self.val_transform,)
        self.val_dataset = torchvision.datasets.MNIST(root='data/',
                                            train=False,
                                            transform=self.val_transform,
                                            download=True)
        
        ## split dataset
        if args.train_size != -1:
            indices = list(range(len(self.train_dataset)))
            np.random.shuffle(indices)
            train_idx = indices[:args.train_size]
            self.train_dataset = Subset(self.train_dataset, train_idx)
            #self.train_val_dataset = Subset(self.train_val_dataset, train_idx)

        super().__init__(args)

class FashionMNIST(Dataset):
    def __init__(self, args):
        self.num_classes = 10
        self.img_size = 28
        self.num_channels = 1

        self.train_transform = transforms.Compose([])
        self.train_transform.transforms.append(transforms.RandomAffine([-15,15], scale=(0.8, 1.2)))
        self.train_transform.transforms.append(transforms.ToTensor())
        self.train_transform.transforms.append(transforms.Normalize((0.1307,), (0.3081,)))
        self.val_transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))])

        self.train_dataset = torchvision.datasets.FashionMNIST(root='data/',
                                            train=True,
                                            download=True,
                                            transform=self.train_transform,)
        self.train_val_dataset = torchvision.datasets.FashionMNIST(root='data/',
                                            train=True,
                                            download=True,
                                            transform=self.val_transform,)
        self.val_dataset = torchvision.datasets.FashionMNIST(root='data/',
                                            train=False,
                                            transform=self.val_transform,
                                            download=True)
        
        if args.train_size != -1:
            indices = list(range(len(self.train_dataset)))
            np.random.shuffle(indices)
            train_idx = indices[:args.train_size]
            self.train_dataset = Subset(self.train_dataset, train_idx)
            
        super().__init__(args)

class CIFAR10(Dataset):
    def __init__(self, args):
        self.num_classes = 10
        self.num_channels = 3
        self.img_size = 32

        self.create_transform(args)
        self.train_transform.transforms.append(Cutout(n_holes=1, length=16))

        self.train_dataset = torchvision.datasets.CIFAR10(root='data/',
                                            train=True,
                                            download=True,
                                            transform=self.train_transform,)
        self.train_val_dataset = torchvision.datasets.CIFAR10(root='data/',
                                            train=True,
                                            download=True,
                                            transform=self.val_transform,)
        self.val_dataset = torchvision.datasets.CIFAR10(root='data/',
                                            train=False,
                                            download=True,
                                            transform=self.val_transform)
        
        super().__init__(args)

class CIFAR100(Dataset):
    def __init__(self, args):
        self.num_classes = 100
        self.img_size = 32
        self.num_channels = 3
        self.create_transform(args)
        self.train_transform.transforms.append(Cutout(n_holes=1, length=8))

        self.train_dataset = torchvision.datasets.CIFAR100(root='data/',
                                            train=True,
                                            download=True,
                                            transform=self.train_transform,)
        self.train_val_dataset = torchvision.datasets.CIFAR100(root='data/',
                                            train=True,
                                            download=True,
                                            transform=self.val_transform,)
        self.val_dataset = torchvision.datasets.CIFAR100(root='data/',
                                            train=False,
                                            transform=self.val_transform,
                                            download=True)
        super().__init__(args)

class SVHN(Dataset):
    def __init__(self, args):
        self.num_classes = 10
        self.img_size = 32
        self.create_transform(args)

        if args.cutout:
            if args.length is None:
                args.length=20
            self.train_transform.transforms.append(Cutout(n_holes=args.n_holes, length=args.length))

        # train dataset
        self.train_dataset = torchvision.datasets.SVHN(root='data/',
                                        split='train',
                                        transform=self.train_transform,
                                        download=True)

        self.extra_dataset = torchvision.datasets.SVHN(root='data/',
                                        split='extra',
                                        transform=self.train_transform,
                                        download=True)

        # Combine both training splits (https://arxiv.org/pdf/1605.07146.pdf)
        data = np.concatenate([self.train_dataset.data, self.extra_dataset.data], axis=0)
        labels = np.concatenate([self.train_dataset.labels, self.extra_dataset.labels], axis=0)
        self.train_dataset.data = data
        self.train_dataset.labels = labels

        # val dataset
        self.train_val_dataset = torchvision.datasets.SVHN(root='data/',
                                        split='train',
                                        transform=self.val_transform,
                                        download=True)

        self.val_extra_dataset = torchvision.datasets.SVHN(root='data/',
                                        split='extra',
                                        transform=self.val_transform,
                                        download=True)

        # Combine both training splits (https://arxiv.org/pdf/1605.07146.pdf)
        data = np.concatenate([self.train_val_dataset.data, self.val_extra_dataset.data], axis=0)
        labels = np.concatenate([self.train_val_dataset.labels, self.val_extra_dataset.labels], axis=0)
        self.train_val_dataset.data = data
        self.train_val_dataset.labels = labels

        self.val_dataset = torchvision.datasets.SVHN(root='data/',
                                        split='test',
                                        transform=self.val_transform,
                                        download=True)
        super().__init__(args)

class Cars(Dataset):
    def __init__(self, args):
        self.num_classes = 196
        self.img_size = 32
        self.create_transform(args)

        #if args.cutout:
        #    if args.length is None:
        #        args.length=8
        #    self.train_transform.transforms.append(Cutout(n_holes=args.n_holes, length=args.length))

        self.train_dataset = torchvision.datasets.StanfordCars(root='data/',
                                            split='train',
                                            download=True,
                                            transform=self.train_transform,)
        self.train_val_dataset = torchvision.datasets.StanfordCars(root='data/',
                                            split='train',
                                            download=True,
                                            transform=self.val_transform,)
        self.val_dataset = torchvision.datasets.StanfordCars(root='data/',
                                            split='test',
                                            download=True,
                                            transform=self.val_transform,)
        super().__init__(args)

class Flowers(Dataset):
    def __init__(self, args):
        self.num_classes = 102
        self.img_size = 30
        self.create_transform(args)

        #if args.cutout:
        #    if args.length is None:
        #        args.length=8
        #    self.train_transform.transforms.append(Cutout(n_holes=args.n_holes, length=args.length))

        self.train_dataset = torchvision.datasets.Flowers102(root='data/',
                                            split="train",
                                            download=True,
                                            transform=self.train_transform,)
        self.train_val_dataset = torchvision.datasets.Flowers102(root='data/',
                                            split="train",
                                            download=True,
                                            transform=self.val_transform,)
        self.val_dataset = torchvision.datasets.Flowers102(root='data/',
                                            split="val",
                                            download=True,
                                            transform=self.val_transform,)
        super().__init__(args)

class INat2019(Dataset):
    def __init__(self, args):
        self.num_classes = 102
        self.img_size = 30
        self.create_transform(args)

        if args.cutout:
            if args.length is None:
                args.length=8
            self.train_transform.transforms.append(Cutout(n_holes=args.n_holes, length=args.length))

        self.train_dataset = INatDataset(root='data/',
                                            train=True,
                                            download=True,
                                            year=2019,
                                            transform=self.train_transform,)
        self.train_val_dataset = INatDataset(root='data/',
                                            train=True,
                                            download=True,
                                            year=2019,
                                            transform=self.val_transform,)
        self.val_dataset = INatDataset(root='data/',
                                        train=False,
                                        download=True,
                                        year=2019,
                                        transform=self.val_transform,)
        super().__init__(args)

class INatDataset(ImageFolder):
    def __init__(self, root, train=True, year=2019, transform=None, target_transform=None,
                 category='name', loader=default_loader):
        self.transform = transform
        self.loader = loader
        self.target_transform = target_transform
        self.year = year
        # assert category in ['kingdom','phylum','class','order','supercategory','family','genus','name']
        path_json = os.path.join(root, f'{"train" if train else "val"}{year}.json')
        with open(path_json) as json_file:
            data = json.load(json_file)

        with open(os.path.join(root, 'categories.json')) as json_file:
            data_catg = json.load(json_file)

        path_json_for_targeter = os.path.join(root, f"train{year}.json")

        with open(path_json_for_targeter) as json_file:
            data_for_targeter = json.load(json_file)

        targeter = {}
        indexer = 0
        for elem in data_for_targeter['annotations']:
            king = []
            king.append(data_catg[int(elem['category_id'])][category])
            if king[0] not in targeter.keys():
                targeter[king[0]] = indexer
                indexer += 1
        self.nb_classes = len(targeter)

        self.samples = []
        for elem in data['images']:
            cut = elem['file_name'].split('/')
            target_current = int(cut[2])
            path_current = os.path.join(root, cut[0], cut[2], cut[3])

            categors = data_catg[target_current]
            target_current_true = targeter[categors[category]]
            self.samples.append((path_current, target_current_true))