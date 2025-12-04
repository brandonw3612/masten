import argparse, torch
import diffusion.linearized as dl
from diffusion.linearized.preserved_tokens import PreservedTokens

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, required=True, help='Path to the dataset checkpoint file')
    parser.add_argument('--model', type=str, required=True, help='Path to save/load the model checkpoint file')
    parser.add_argument('--epochs', type=int, default=300)
    parser.add_argument('--batch-size', type=int, default=512)
    parser.add_argument('--learning-rate', type=float, default=1e-3)
    parser.add_argument('--sdl', type=float, default=2.0, help='Structured Diffusion Loss weight')
    args = parser.parse_args()

    device = torch.accelerator.current_accelerator()
    print('Using torch device: ', device)

    dataset = dl.LinearizedDataset.from_checkpoint(args.dataset)

    print(f'Loaded dataset with {len(dataset)} samples')
    print(f'Vocab size: {dataset.tokenizer.vocab_size}, Max length: {dataset.tokenizer.max_len}')

    model = dl.DiffusionTransformer(
        dataset.tokenizer.vocab_size,
        dataset.tokenizer.max_len,
        embed_dim=512,
        num_heads=8,
        num_layers=8
    ).to(device)
    criterion = dl.StructuredDiffusionLoss(
        eos_id=dataset.tokenizer.token_to_index[PreservedTokens.EOS],
        pad_id=dataset.tokenizer.token_to_index[PreservedTokens.PAD],
        lambda_struct=args.sdl
    ).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate)

    dl.train(
        dataset, model, optimizer, criterion, device,
        args.epochs, args.batch_size,
        args.model
    )