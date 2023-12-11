import utils
import argparse

def main(args):
    conn, cur = utils.get_db(args.config)
    utils.create_tables(conn, cur)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="configs/db_aws.yaml")
    args = parser.parse_args()
    main(args)