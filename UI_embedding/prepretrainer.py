
import torch
import torch.nn as nn
from torch.optim import Adam
from torch.utils.data import DataLoader

from UI2Vec import UI2Vec
from prediction import HiddenLabelPredictorModel
from dataset.vocab import BertScreenVocab

class UI2VecTrainer:
    """
    """

    def __init__(self, embedder: UI2Vec, predictor: HiddenLabelPredictorModel, dataloader_train, dataloader_test, 
                vocab: BertScreenVocab, vocab_size:int, l_rate: float, n: int, bert_size=768):
        """
        """
        self.loss = nn.CosineEmbeddingLoss()
        self.UI2Vec = embedder
        self.predictor = predictor
        self.optimizer = Adam(self.predictor.parameters())
        self.vocab = vocab
        self.train_data = dataloader_train
        self.test_data = dataloader_test
        self.vocab_size = vocab_size

    def train(self, epoch):
        self.iteration(epoch, self.train_data)

    def test(self, epoch):
        self.iteration(epoch, self.test_data, train=False)

    def iteration(self, epoch, data_loader: iter, train=True):
        """
        loop over the data_loader for training or testing
        if train , backward operation is activated
        also auto save the model every epoch

        :param epoch: index of current epoch 
        :param data_loader: torch.utils.data.DataLoader for iteration
        :param train: boolean value of is train or test
        :return: None
        """
        total_loss = 0
        total_data = 0
        # iterate through data_loader
        for data in data_loader:
            total_data+=1
            element = data[0]
            context = data[1]
            # load data properly
            # forward the training stuff (prediction models)
            prediction_output = self.predictor.forward(context) #input here
            element_target_index = self.vocab.get_index(element[0])
            element_target_emb = self.vocab.get_embedding(element_target_index)
            # calculate NLL loss for all prediction stuff
            prediction_loss = self.loss(prediction_output, element_target_emb, torch.ones(#batchsize)) #TODO: make 1, -1 into tensors, may need to switch places
            for index in range(self.vocab_size):
                if index != element_target_index:
                    prediction_loss+= self.loss(prediction_output, self.vocab.get_embedding(index), -1)
            # if in train, backwards and optimization
            total_loss+=prediction_loss
            if train:
                self.optimizer.zero_grad()
                prediction_loss.backward()
                self.optimizer.step()
        return total_loss/total_data

    def save(self, epoch, file_path="output/trained.model"):
        """
        Saving the current model on file_path
        :param epoch: current epoch number
        :param file_path: model output path which gonna be file_path+"ep%d" % epoch
        :return: final_output_path
        """
        output_path = file_path + ".ep%d" % epoch
        torch.save(self.UI2Vec.cpu(), output_path)
        self.bert.to(self.device)
        print("EP:%d Model Saved on:" % epoch, output_path)
        return output_path